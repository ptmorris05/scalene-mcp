"""Scalene profiler wrapper and execution logic."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any

from scalene_mcp.models import ProfileResult
from scalene_mcp.parser import ProfileParser


class ScaleneProfiler:
    """Wrapper for running Scalene profiler asynchronously."""

    async def profile_script(
        self,
        script_path: Path | str,
        *,
        # What to profile
        cpu: bool = True,
        memory: bool = True,
        gpu: bool = False,
        # Profiling modes
        cpu_only: bool = False,
        stacks: bool = False,
        use_virtual_time: bool = False,
        # Sampling & thresholds
        cpu_sampling_rate: float = 0.01,
        cpu_percent_threshold: float = 1.0,
        malloc_threshold: int = 100,
        allocation_sampling_window: int = 10485767,
        # Scope control
        profile_all: bool = False,
        profile_only: str = "",
        profile_exclude: str = "",
        # Analysis
        memory_leak_detector: bool = True,
        reduced_profile: bool = False,
        # Script arguments
        script_args: list[str] | None = None,
        # Execution
        timeout: float | None = None,
    ) -> ProfileResult:
        """
        Run Scalene profiler on a script.

        Args:
            script_path: Path to the Python script to profile
            cpu: Enable CPU profiling
            memory: Enable memory profiling
            gpu: Enable GPU profiling
            cpu_only: CPU-only mode (faster)
            stacks: Collect stack traces
            use_virtual_time: Use virtual time instead of wall clock
            cpu_sampling_rate: CPU sampling rate in seconds
            cpu_percent_threshold: Minimum CPU % to report
            malloc_threshold: Minimum allocation size to report (bytes)
            allocation_sampling_window: Memory allocation sampling window
            profile_all: Profile all code (not just target script)
            profile_only: Profile only these paths (comma-separated)
            profile_exclude: Exclude these paths (comma-separated)
            memory_leak_detector: Enable leak detection
            reduced_profile: Reduced profile output (thresholds applied)
            script_args: Arguments to pass to the script
            timeout: Timeout in seconds (None for no timeout)

        Returns:
            ProfileResult object with parsed profiling data

        Raises:
            FileNotFoundError: If script doesn't exist
            RuntimeError: If profiling fails
            asyncio.TimeoutError: If profiling times out
        """
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        # Use temp file with auto-cleanup
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            prefix="scalene_",
            delete=False,  # Keep file until we parse it
        ) as tmp_file:
            output_file = Path(tmp_file.name)

        try:
            # Build Scalene command
            cmd = [
                "python",
                "-m",
                "scalene",
                "run",  # Scalene v2+ requires 'run' subcommand
                "--json",
                "--outfile",
                str(output_file),
                "--no-browser",
            ]

            # Profiling modes
            if cpu_only:
                cmd.append("--cpu-only")
            if not cpu:
                cmd.append("--no-cpu")
            if not memory:
                cmd.append("--no-memory")
            if gpu:
                cmd.append("--gpu")

            # Advanced options
            if stacks:
                cmd.append("--stacks")
            if use_virtual_time:
                cmd.append("--use-virtual-time")
            if not memory_leak_detector:
                cmd.append("--no-memory-leak-detector")
            if reduced_profile:
                cmd.append("--reduced-profile")

            # Sampling and thresholds
            if cpu_sampling_rate != 0.01:
                cmd.extend(["--cpu-sampling-rate", str(cpu_sampling_rate)])
            if cpu_percent_threshold != 1.0:
                cmd.extend(["--cpu-percent-threshold", str(cpu_percent_threshold)])
            if malloc_threshold != 100:
                cmd.extend(["--malloc-threshold", str(malloc_threshold)])
            if allocation_sampling_window != 10485767:
                cmd.extend(
                    ["--allocation-sampling-window", str(allocation_sampling_window)]
                )

            # Scope control
            if profile_all:
                cmd.append("--profile-all")
            if profile_only:
                cmd.extend(["--profile-only", profile_only])
            if profile_exclude:
                cmd.extend(["--profile-exclude", profile_exclude])

            # Add script path
            cmd.append(str(script_path))

            # Add script arguments
            if script_args:
                cmd.append("---")  # Scalene separator for script args
                cmd.extend(script_args)

            # Run profiler
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            if timeout:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            else:
                stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise RuntimeError(
                    f"Scalene profiling failed (exit code {process.returncode}): "
                    f"{stderr.decode()}"
                )

            if not output_file.exists():
                raise RuntimeError(
                    f"Scalene did not create output file: {output_file}"
                )

            # Parse JSON immediately
            parser = ProfileParser()
            profile_result = parser.parse_file(output_file)
            
            return profile_result

        except asyncio.TimeoutError:
            # Kill the process if it times out
            try:
                process.kill()
                await process.wait()
            except Exception:
                pass
            raise asyncio.TimeoutError(
                f"Profiling timed out after {timeout} seconds"
            )
        
        finally:
            # Always clean up temp file
            output_file.unlink(missing_ok=True)

    async def profile_code(
        self,
        code: str,
        **kwargs: Any,
    ) -> ProfileResult:
        """
        Profile a code snippet.

        Args:
            code: Python code to profile
            **kwargs: Arguments passed to profile_script()

        Returns:
            ProfileResult object with parsed profiling data

        Raises:
            RuntimeError: If profiling fails
        """
        # Create temporary script file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            prefix="scalene_snippet_",
            delete=False,
        ) as f:
            f.write(code)
            script_path = Path(f.name)

        try:
            return await self.profile_script(script_path, **kwargs)
        finally:
            # Clean up temporary script file
            script_path.unlink(missing_ok=True)


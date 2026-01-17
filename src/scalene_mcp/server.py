"""Scalene MCP Server.

Main FastMCP server with tools, resources, and prompts for Scalene profiling.
"""

import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from scalene_mcp.logging import get_logger

from .analyzer import ProfileAnalyzer
from .comparator import ProfileComparator
from .models import ProfileResult
from .parser import ProfileParser
from .profiler import ScaleneProfiler

# Create the MCP server
server = FastMCP("Scalene Profiler")

# Initialize components
profiler = ScaleneProfiler()
parser = ProfileParser()
analyzer = ProfileAnalyzer()
comparator = ProfileComparator()

# Store recent profiles (in-memory for now)
recent_profiles: dict[str, ProfileResult] = {}

# Project context (auto-detected or explicitly set)
_project_root: Path | None = None

logger = get_logger(__name__)


def _detect_project_root(start_path: Path | None = None) -> Path:
    """Auto-detect project root by looking for common markers.
    
    Checks for: .git, pyproject.toml, setup.py, package.json, Makefile
    Falls back to current working directory if no markers found.
    """
    search_path = start_path or Path.cwd()
    if search_path.is_file():
        search_path = search_path.parent
    
    markers = {".git", "pyproject.toml", "setup.py", "package.json", "Makefile", "GNUmakefile"}
    
    # Search up directory tree
    for current in [search_path, *search_path.parents]:
        if any((current / marker).exists() for marker in markers):
            return current
    
    # Fallback to cwd
    return Path.cwd()


def _get_project_root() -> Path:
    """Get the current project root (auto-detected or explicitly set)."""
    global _project_root
    if _project_root is None:
        _project_root = _detect_project_root()
    return _project_root


def _resolve_path(relative_or_absolute: str) -> Path:
    """Resolve a path, making it absolute relative to project root if needed."""
    path = Path(relative_or_absolute)
    if path.is_absolute():
        return path
    return _get_project_root() / path


# ============================================================================
# Discovery Tools - Help LLM understand the project context
# ============================================================================


async def get_project_root() -> dict[str, str]:
    """Get the detected project root and structure type.
    
    Returns: {root, type, markers_found}
    """
    root = _get_project_root()
    
    # Detect project type
    project_type = "unknown"
    markers_found = []
    
    if (root / "pyproject.toml").exists():
        project_type = "python"
        markers_found.append("pyproject.toml")
    if (root / "setup.py").exists():
        project_type = "python"
        markers_found.append("setup.py")
    if (root / "package.json").exists():
        project_type = "node" if project_type == "unknown" else "mixed"
        markers_found.append("package.json")
    if (root / ".git").exists():
        markers_found.append(".git")
    if (root / "Makefile").exists():
        markers_found.append("Makefile")
    if (root / "GNUmakefile").exists():
        markers_found.append("GNUmakefile")
    
    return {
        "root": str(root.absolute()),
        "type": project_type,
        "markers_found": ", ".join(markers_found) if markers_found else "none",
    }


server.tool(get_project_root)


async def list_project_files(
    pattern: str = "*.py",
    max_depth: int = 3,
    exclude_patterns: str = ".git,__pycache__,node_modules,.venv,venv",
) -> list[str]:
    """List project files matching pattern, relative to project root.
    
    Args:
        pattern: Glob pattern (*.py, src/**, etc.)
        max_depth: Maximum directory depth to search
        exclude_patterns: Comma-separated patterns to exclude
        
    Returns: [relative_path, ...] sorted alphabetically
    """
    root = _get_project_root()
    exclude = {s.strip() for s in exclude_patterns.split(",") if s.strip()}
    
    def should_exclude(p: Path) -> bool:
        """Check if path should be excluded."""
        return any(part in exclude for part in p.parts)
    
    results = []
    
    # Handle different pattern types
    if "**" in pattern:
        # Recursive glob
        glob_pattern = pattern
    else:
        # Non-recursive, search at all depths
        glob_pattern = f"**/{pattern}"
    
    for file_path in sorted(root.glob(glob_pattern)):
        if file_path.is_file() and not should_exclude(file_path):
            try:
                rel_path = file_path.relative_to(root)
                depth = len(rel_path.parts)
                if depth <= max_depth:
                    results.append(str(rel_path))
            except ValueError:
                pass
    
    return sorted(results)


server.tool(list_project_files)


async def set_project_context(project_root: str) -> dict[str, str]:
    """Explicitly set the project root (overrides auto-detection).
    
    Use this if auto-detection fails or gives wrong path.
    
    Args:
        project_root: Absolute path to project root
        
    Returns: {project_root, status}
    """
    global _project_root
    path = Path(project_root)
    if not path.exists():
        raise ValueError(f"Path does not exist: {project_root}")
    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {project_root}")
    
    _project_root = path
    return {
        "project_root": str(path.absolute()),
        "status": "set",
    }


server.tool(set_project_context)


# ============================================================================
# Profiling Tools
# ============================================================================


async def profile_script(
    script_path: str,
    cpu_only: bool = False,
    include_memory: bool = True,
    include_gpu: bool = False,
    reduced_profile: bool = False,
    profile_only: str = "",
    profile_exclude: str = "",
    use_virtual_time: bool = False,
    cpu_percent_threshold: float = 1.0,
    malloc_threshold: int = 100,
    script_args: list[str] | None = None,
) -> dict[str, Any]:
    """Profile a Python script using Scalene.
    
    Args:
        script_path: Path to Python script (absolute or relative to project root)
        cpu_only: Measure CPU time only
        include_memory: Profile memory allocations
        include_gpu: Profile GPU usage (requires NVIDIA GPU)
        reduced_profile: Show only lines with >1% CPU or >100 allocations
        profile_only: Comma-separated paths to include (e.g., "myapp")
        profile_exclude: Comma-separated paths to exclude (e.g., "test,vendor")
        use_virtual_time: Measure CPU time excluding I/O wait
        cpu_percent_threshold: Minimum CPU % to report
        malloc_threshold: Minimum allocation bytes to report
        script_args: Command-line arguments for the script
        
    Returns: {profile_id, summary, text_summary}
    """
    path = _resolve_path(script_path)
    if not path.exists():
        raise FileNotFoundError(f"Script not found: {path}")

    # Run profiler
    profile = await profiler.profile_script(
        path,
        cpu_only=cpu_only,
        memory=include_memory and not cpu_only,
        gpu=include_gpu,
        reduced_profile=reduced_profile,
        profile_only=profile_only,
        profile_exclude=profile_exclude,
        use_virtual_time=use_virtual_time,
        cpu_percent_threshold=cpu_percent_threshold,
        malloc_threshold=malloc_threshold,
        script_args=script_args or [],
    )

    # Store profile
    profile_id = profile.profile_id or f"profile_{len(recent_profiles)}"
    recent_profiles[profile_id] = profile

    # Return summary
    return {
        "profile_id": profile_id,
        "summary": profile.summary.model_dump(),
        "text_summary": analyzer.generate_summary(profile),
    }


# Register tool
server.tool(profile_script)


async def profile_code(
    code: str,
    cpu_only: bool = False,
    include_memory: bool = True,
    reduced_profile: bool = False,
) -> dict[str, Any]:
    """Profile Python code snippet without saving to file.
    
    Args:
        code: Python code to execute and profile
        cpu_only: Measure CPU time only
        include_memory: Profile memory allocations
        reduced_profile: Show only significant lines
        
    Returns: {profile_id, summary, text_summary}
    """
    # Run profiler
    profile = await profiler.profile_code(
        code,
        cpu_only=cpu_only,
        memory=include_memory and not cpu_only,
        reduced_profile=reduced_profile,
    )

    # Store profile
    profile_id = profile.profile_id or f"profile_{len(recent_profiles)}"
    recent_profiles[profile_id] = profile

    return {
        "profile_id": profile_id,
        "summary": profile.summary.model_dump(),
        "text_summary": analyzer.generate_summary(profile),
    }


server.tool(profile_code)


async def analyze_profile(
    profile_id: str,
    focus: str = "all",
    top_n: int = 10,
    cpu_threshold: float = 5.0,
    memory_threshold_mb: float = 10.0,
) -> dict[str, Any]:
    """Analyze a profile for bottlenecks and recommendations.
    
    Args:
        profile_id: ID from profile_script or profile_code
        focus: "cpu", "memory", "gpu", or "all"
        top_n: Number of hotspots to return
        cpu_threshold: Minimum CPU % to flag as bottleneck
        memory_threshold_mb: Minimum MB to flag as bottleneck
        
    Returns: {focus, hotspots, bottlenecks, recommendations, summary}
    """
    if profile_id not in recent_profiles:
        raise ValueError(f"Profile not found: {profile_id}")

    profile = recent_profiles[profile_id]
    analysis = analyzer.analyze(
        profile,
        top_n=top_n,
        cpu_threshold=cpu_threshold,
        memory_threshold_mb=memory_threshold_mb,
        focus=focus,
    )

    return analysis.model_dump()


server.tool(analyze_profile)


async def get_cpu_hotspots(
    profile_id: str,
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """Get lines using the most CPU time.
    
    Args:
        profile_id: ID from profile_script or profile_code
        top_n: Number of hotspots to return
        
    Returns: [{type, filename, lineno, line, cpu_percent, severity}, ...]
    """
    if profile_id not in recent_profiles:
        raise ValueError(f"Profile not found: {profile_id}")

    profile = recent_profiles[profile_id]
    hotspots = analyzer.get_top_cpu_hotspots(profile, n=top_n)

    return [hotspot.model_dump() for hotspot in hotspots]


server.tool(get_cpu_hotspots)


async def get_memory_hotspots(
    profile_id: str,
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """Get lines allocating the most memory.
    
    Args:
        profile_id: ID from profile_script or profile_code
        top_n: Number of hotspots to return
        
    Returns: [{type, filename, lineno, line, memory_mb, severity}, ...]
    """
    if profile_id not in recent_profiles:
        raise ValueError(f"Profile not found: {profile_id}")

    profile = recent_profiles[profile_id]
    hotspots = analyzer.get_top_memory_hotspots(profile, n=top_n)

    return [hotspot.model_dump() for hotspot in hotspots]


server.tool(get_memory_hotspots)


async def get_gpu_hotspots(
    profile_id: str,
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """Get lines using the most GPU time (CUDA only).
    
    Args:
        profile_id: ID from profile_script or profile_code
        top_n: Number of hotspots to return
        
    Returns: [{type, filename, lineno, line, gpu_percent}, ...]
    """
    if profile_id not in recent_profiles:
        raise ValueError(f"Profile not found: {profile_id}")

    profile = recent_profiles[profile_id]
    hotspots = analyzer.get_top_gpu_hotspots(profile, n=top_n)

    return [hotspot.model_dump() for hotspot in hotspots]


server.tool(get_gpu_hotspots)


async def get_bottlenecks(
    profile_id: str,
    cpu_threshold: float = 5.0,
    memory_threshold_mb: float = 10.0,
) -> dict[str, list[dict[str, Any]]]:
    """Get lines exceeding performance thresholds.
    
    Args:
        profile_id: ID from profile_script or profile_code
        cpu_threshold: Minimum CPU % to flag as bottleneck
        memory_threshold_mb: Minimum MB to flag as bottleneck
        
    Returns: {cpu: [...], memory: [...], gpu: [...]}
    """
    if profile_id not in recent_profiles:
        raise ValueError(f"Profile not found: {profile_id}")

    profile = recent_profiles[profile_id]
    return analyzer.identify_bottlenecks(
        profile,
        cpu_threshold=cpu_threshold,
        memory_threshold_mb=memory_threshold_mb,
    )


server.tool(get_bottlenecks)


async def get_memory_leaks(
    profile_id: str,
) -> list[dict[str, Any]]:
    """Detect likely memory leaks (growing allocations).
    
    Args:
        profile_id: ID from profile_script or profile_code
        
    Returns: [{filename, lineno, line, velocity_mb_per_sec, likelihood_pct}, ...]
    """
    if profile_id not in recent_profiles:
        raise ValueError(f"Profile not found: {profile_id}")

    profile = recent_profiles[profile_id]
    return [leak.model_dump() for leak in profile.summary.detected_leaks]


server.tool(get_memory_leaks)


async def compare_profiles(
    before_id: str,
    after_id: str,
) -> dict[str, Any]:
    """Compare two profiles to measure optimization impact.
    
    Args:
        before_id: Profile ID from original code
        after_id: Profile ID from optimized code
        
    Returns: {runtime_change_pct, memory_change_pct, improvements, regressions, summary_text}
    """
    if before_id not in recent_profiles:
        raise ValueError(f"Profile not found: {before_id}")
    if after_id not in recent_profiles:
        raise ValueError(f"Profile not found: {after_id}")

    before = recent_profiles[before_id]
    after = recent_profiles[after_id]

    comparison = comparator.compare(before, after)
    return comparison.model_dump()


server.tool(compare_profiles)


async def get_file_details(
    profile_id: str,
    filename: str,
) -> dict[str, Any]:
    """Get all metrics for a specific file.
    
    Args:
        profile_id: ID from profile_script or profile_code
        filename: Path to file to analyze
        
    Returns: {filename, lines, total_cpu_percent, total_memory_mb}
    """
    if profile_id not in recent_profiles:
        raise ValueError(f"Profile not found: {profile_id}")

    profile = recent_profiles[profile_id]

    if filename not in profile.files:
        available = list(profile.files.keys())
        raise ValueError(
            f"File not in profile: {filename}. Available: {', '.join(available)}"
        )

    file_metrics = profile.files[filename]
    return file_metrics.model_dump()


server.tool(get_file_details)


async def list_profiles() -> list[str]:
    """List all captured profiles in this session.
    
    Returns: [profile_id, ...]
    """
    return list(recent_profiles.keys())


server.tool(list_profiles)


async def get_recommendations(
    profile_id: str,
) -> list[str]:
    """Get actionable optimization suggestions.
    
    Args:
        profile_id: ID from profile_script or profile_code
        
    Returns: [recommendation_text, ...]
    """
    if profile_id not in recent_profiles:
        raise ValueError(f"Profile not found: {profile_id}")

    profile = recent_profiles[profile_id]
    return analyzer.generate_recommendations(profile)


server.tool(get_recommendations)


async def get_function_summary(
    profile_id: str,
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """Get function-level performance metrics.
    
    Args:
        profile_id: ID from profile_script or profile_code
        top_n: Number of functions to return
        
    Returns: [{function_name, filename, start_line, total_cpu_percent, total_memory_mb}, ...]
    """
    if profile_id not in recent_profiles:
        raise ValueError(f"Profile not found: {profile_id}")

    profile = recent_profiles[profile_id]
    return analyzer.get_function_summary(profile, top_n=top_n)


server.tool(get_function_summary)


def main() -> None:
    """Entry point for running the server."""
    server.run()


if __name__ == "__main__":
    main()

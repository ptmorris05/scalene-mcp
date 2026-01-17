"""Scalene MCP Server.

Main FastMCP server with tools, resources, and prompts for Scalene profiling.
"""

from pathlib import Path
from typing import Any

from fastmcp import FastMCP

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
    """
    Profile a Python script to identify performance bottlenecks, memory usage, and optimization opportunities.

    Use this tool to analyze where your Python code spends time (CPU), allocates memory, or uses GPU resources.
    The profiler runs your script and captures detailed line-by-line metrics.

    **When to use**: When you need to understand which parts of a Python script are slow or memory-intensive.
    **Returns**: A profile_id for querying results, plus a human-readable summary showing hotspots and issues.

    Args:
        script_path: Absolute or relative path to the Python script (e.g., "./my_script.py" or "/path/to/script.py")
        cpu_only: Set True for faster profiling that only measures CPU time (skips memory profiling)
        include_memory: Set False to disable memory profiling (use with cpu_only=True for fastest profiling)
        include_gpu: Set True to profile GPU usage (requires NVIDIA GPU with CUDA)
        reduced_profile: Set True to show only lines using >1% CPU or >100 allocations (cleaner output for large codebases)
        profile_only: Comma-separated paths to include (e.g., "mypackage,mymodule" profiles only those files)
        profile_exclude: Comma-separated paths to exclude (e.g., "test,vendor" skips test and vendor code)
        use_virtual_time: Set True to measure only CPU time, excluding I/O wait time (useful for I/O-heavy code)
        cpu_percent_threshold: Minimum CPU % to report (default 1.0, lower values show more detail)
        malloc_threshold: Minimum allocation size in bytes to report (default 100)
        script_args: List of command-line arguments to pass to the script (e.g., ["--input", "data.csv"])

    Returns:
        Dictionary with:
        - profile_id: Unique ID to query this profile's results with other tools
        - summary: Structured data (total time, memory, GPU, detected leaks)
        - text_summary: Human-readable Markdown summary with key findings and hotspots

    Example:
        To profile a script that takes arguments:
        profile_script("/home/user/analyze.py", script_args=["--file", "data.csv", "--verbose"])

        To profile only your application code (skip libraries):
        profile_script("app.py", profile_only="myapp", reduced_profile=True)
    """
    path = Path(script_path)
    if not path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

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
    """
    Profile a Python code snippet to identify performance issues without saving to a file.

    Use this tool when you want to quickly test a code fragment or compare different implementations.
    The code is executed in a temporary environment and profiled line-by-line.

    **When to use**: When testing small code snippets, comparing algorithms, or prototyping optimizations.
    **Returns**: A profile_id for querying results, plus a summary of performance characteristics.

    Args:
        code: Complete Python code to execute and profile (must be valid Python)
        cpu_only: Set True for faster profiling that only measures CPU time
        include_memory: Set False to disable memory profiling
        reduced_profile: Set True to show only significant lines (>1% CPU or >100 allocations)

    Returns:
        Dictionary with:
        - profile_id: Unique ID to query this profile's results
        - summary: Structured performance data
        - text_summary: Human-readable analysis with hotspots and recommendations

    Example:
        Profile a function to see if list comprehension is faster:
        code = '''\n# Compare list comprehension vs loop\ndata = range(10000)\nresult = [x**2 for x in data]  # vs: result = []; for x in data: result.append(x**2)\n'''
        profile_code(code, cpu_only=True)
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
    """
    Get detailed analysis and recommendations for a previously captured profile.

    Use this after profile_script or profile_code to get structured insights about performance issues,
    bottlenecks, and actionable optimization suggestions.

    **When to use**: After profiling, to understand what to optimize and get specific recommendations.
    **Returns**: Detailed breakdown of hotspots, bottlenecks, memory leaks, and optimization advice.

    Args:
        profile_id: ID returned from profile_script or profile_code
        focus: What to analyze - "cpu" (time spent), "memory" (allocations), "gpu" (GPU usage), or "all" (everything)
        top_n: How many worst offenders to return (e.g., top 10 slowest lines)
        cpu_threshold: Only flag bottlenecks using more than this % of CPU time (lower = more sensitive)
        memory_threshold_mb: Only flag bottlenecks allocating more than this many MB (lower = more sensitive)

    Returns:
        Dictionary with:
        - focus: What was analyzed
        - hotspots: List of specific problematic lines with file, line number, and metrics
        - bottlenecks: Categorized issues (CPU-intensive lines, memory-heavy allocations, GPU usage)
        - recommendations: Actionable suggestions like "optimize this loop" or "reduce allocations here"
        - summary: Formatted text explaining the analysis

    Example:
        After profiling, get CPU-focused analysis:
        result = profile_script("slow_script.py")
        analysis = analyze_profile(result["profile_id"], focus="cpu", top_n=5, cpu_threshold=2.0)
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
    """
    Identify the lines of code that consume the most CPU time.

    Use this to find where your program is spending the most execution time. Each hotspot shows
    the exact file, line number, source code, and what percentage of total CPU time it consumes.

    **When to use**: When you know CPU time is the problem and want to see exactly which lines are slowest.
    **Returns**: Sorted list of the slowest code locations, ranked by CPU time percentage.

    Args:
        profile_id: ID returned from profile_script or profile_code
        top_n: Maximum number of hotspots to return (e.g., 10 for top 10 slowest lines)

    Returns:
        List of dictionaries, each containing:
        - type: "cpu"
        - filename: Source file path
        - lineno: Line number in the file
        - line: Actual source code text
        - cpu_percent: What % of total CPU time this line used
        - severity: "critical", "high", "medium", or "low"

    Example:
        Find the 5 slowest lines in a profile:
        hotspots = get_cpu_hotspots(profile_id, top_n=5)
        for spot in hotspots:
            print(f"{spot['filename']}:{spot['lineno']} uses {spot['cpu_percent']}% CPU")
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
    """
    Identify the lines of code that allocate the most memory.

    Use this to find where your program is creating objects, allocating buffers, or building large data structures.
    Shows both Python memory (objects, lists, dicts) and native memory (NumPy arrays, C extensions).

    **When to use**: When memory usage is high or growing, to find which lines are allocating the most.
    **Returns**: Sorted list of the most memory-intensive lines, ranked by total MB allocated.

    Args:
        profile_id: ID returned from profile_script or profile_code
        top_n: Maximum number of hotspots to return

    Returns:
        List of dictionaries, each containing:
        - type: "memory"
        - filename: Source file path
        - lineno: Line number
        - line: Source code text
        - memory_mb: Total megabytes allocated at this line
        - severity: Impact level

    Example:
        Find memory-intensive lines:
        hotspots = get_memory_hotspots(profile_id, top_n=3)
        if hotspots:
            worst = hotspots[0]
            print(f"Line {worst['lineno']} allocated {worst['memory_mb']} MB")
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
    """
    Identify code lines that use GPU compute resources (NVIDIA CUDA only).

    Use this when profiling code that uses PyTorch, TensorFlow, or other GPU-accelerated libraries.
    Shows which lines are transferring data to/from GPU or running GPU kernels.

    **When to use**: When code uses GPUs and you want to optimize GPU utilization.
    **Returns**: Lines that trigger GPU operations, ranked by GPU time. Empty if no GPU detected.

    Args:
        profile_id: ID returned from profile_script or profile_code (must have been run with include_gpu=True)
        top_n: Maximum number of hotspots to return

    Returns:
        List of dictionaries with:
        - type: "gpu"
        - filename: Source file
        - lineno: Line number
        - line: Source code
        - gpu_percent: What % of GPU time this line used

    Example:
        Profile with GPU enabled and find GPU hotspots:
        result = profile_script("train_model.py", include_gpu=True)
        gpu_lines = get_gpu_hotspots(result["profile_id"])
        if not gpu_lines:
            print("No GPU usage detected - check if CUDA is available")
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
    """
    Identify performance bottlenecks: lines that significantly impact CPU, memory, or GPU.

    Use this to get a filtered view of only the most problematic code. Unlike hotspots which show
    all usage, this only shows lines exceeding the thresholds - the real bottlenecks worth fixing.

    **When to use**: When you want to focus on the worst problems, not every line.
    **Returns**: Categorized lists of CPU, memory, and GPU bottlenecks that exceed thresholds.

    Args:
        profile_id: ID returned from profile_script or profile_code
        cpu_threshold: Only return lines using more than this % of total CPU (e.g., 5.0 = 5%)
        memory_threshold_mb: Only return lines allocating more than this many megabytes

    Returns:
        Dictionary with three keys:
        - "cpu": List of CPU bottlenecks (lines using > cpu_threshold% CPU)
        - "memory": List of memory bottlenecks (lines allocating > memory_threshold_mb MB)
        - "gpu": List of GPU bottlenecks (if GPU profiling was enabled)

        Each bottleneck includes filename, line number, code, metrics, and severity.

    Example:
        Find only severe performance issues:
        bottlenecks = get_bottlenecks(profile_id, cpu_threshold=10.0, memory_threshold_mb=50.0)
        if bottlenecks["cpu"]:
            print(f"Found {len(bottlenecks['cpu'])} CPU bottlenecks using >10% CPU each")
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
    """
    Detect potential memory leaks: allocations that grow continuously without being freed.

    Use this when memory usage keeps increasing over time. Scalene's leak detector identifies
    lines where memory is allocated but never released, which can cause programs to eventually
    crash or slow down from memory pressure.

    **When to use**: When memory usage grows unbounded, or after long-running tests show memory buildup.
    **Returns**: List of suspected leaks with location, growth velocity, and likelihood score.

    Args:
        profile_id: ID returned from profile_script or profile_code

    Returns:
        List of detected memory leaks, each containing:
        - filename: Where the leak originates
        - lineno: Specific line number
        - line: Source code that's leaking
        - mbytes_leaked: Estimated memory growth in MB
        - velocity_mb_per_sec: How fast memory is growing
        - likelihood_pct: Confidence this is a real leak (0-100%)

        Empty list if no leaks detected (good news!).

    Example:
        Check for memory leaks:
        leaks = get_memory_leaks(profile_id)
        if leaks:
            for leak in leaks:
                print(f"Potential leak at {leak['filename']}:{leak['lineno']}")
                print(f"  Growing at {leak['velocity_mb_per_sec']} MB/sec")
        else:
            print("No memory leaks detected")
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
    """
    Compare two profiles to measure the impact of code changes and identify improvements or regressions.

    Use this tool after making optimizations to verify they actually helped. It shows whether runtime decreased,
    memory usage improved, and whether any new issues were introduced.

    **When to use**: After optimizing code, to prove the changes made it faster/more memory-efficient.
    **Returns**: Side-by-side comparison showing what got better (✅) and what got worse (⚠️).

    Args:
        before_id: Profile ID from the original/baseline code (captured before changes)
        after_id: Profile ID from the modified/optimized code (captured after changes)

    Returns:
        Dictionary with:
        - runtime_change_percent: % change in execution time (negative = faster)
        - memory_change_percent: % change in peak memory (negative = less memory)
        - improvements: List of positive changes (e.g., "Runtime decreased by 35%")
        - regressions: List of negative changes (e.g., "Memory increased by 10%")
        - overall_improved: True if changes were net positive
        - summary_text: Human-readable Markdown summary with emojis showing what changed

    Example:
        Measure optimization impact:
        before = profile_script("original.py")
        # ... make optimizations ...
        after = profile_script("optimized.py")
        comparison = compare_profiles(before["profile_id"], after["profile_id"])
        print(comparison["summary_text"])
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
    """
    Get complete line-by-line profiling data for a specific file.

    Use this to see detailed metrics for every line in a file, not just the hotspots. Shows
    CPU time, memory allocations, and execution counts for each line, letting you understand
    the full performance picture of a module or file.

    **When to use**: When you want to see all metrics for a specific file, not just top issues.
    **Returns**: Complete profiling breakdown for every line in the requested file.

    Args:
        profile_id: ID returned from profile_script or profile_code
        filename: Name or path of the file (must match a file in the profile)

    Returns:
        Dictionary containing:
        - filename: The file path
        - lines: Dictionary mapping line numbers to LineMetrics with:
            - line_number: Line number
            - cpu_percent_python: % CPU time in Python code
            - cpu_percent_native: % CPU time in C/native code
            - memory_python_mb: MB allocated by Python objects
            - memory_native_mb: MB allocated by native/C code
            - source_code: The actual source text
        - total_cpu_percent: Sum of all CPU usage in this file
        - total_memory_mb: Sum of all memory allocated in this file

    Example:
        Get detailed view of a specific file:
        details = get_file_details(profile_id, "compute.py")
        for line_num, metrics in details["lines"].items():
            if metrics["cpu_percent_python"] > 1.0:
                print(f"Line {line_num}: {metrics['cpu_percent_python']:.1f}% CPU")
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
    """
    List all profiles currently stored in memory.

    Use this to see what profiles are available for analysis. Profiles persist during the current session
    and are identified by unique IDs. You can use these IDs with other tools like analyze_profile,
    get_cpu_hotspots, or compare_profiles.

    **When to use**: To see what profiles you've captured in this session, or to get IDs for comparison.
    **Returns**: List of all profile IDs that can be queried.

    Returns:
        List of profile ID strings (e.g., ["profile_0", "profile_1", "profile_2"])
        Empty list if no profiles have been captured yet.

    Example:
        Check available profiles before comparing:
        profiles = list_profiles()
        if len(profiles) >= 2:
            compare_profiles(profiles[0], profiles[1])
    """
    return list(recent_profiles.keys())


server.tool(list_profiles)


async def get_recommendations(
    profile_id: str,
) -> list[str]:
    """
    Get AI-generated optimization recommendations based on profiling results.

    Use this to get specific, actionable suggestions for improving code performance. The analyzer
    examines CPU hotspots, memory patterns, and detected leaks to suggest concrete optimizations.

    **When to use**: After profiling, to get guidance on what to optimize and how.
    **Returns**: List of human-readable recommendations ranked by potential impact.

    Args:
        profile_id: ID returned from profile_script or profile_code

    Returns:
        List of recommendation strings, such as:
        - "Line 45 in compute.py: Consider using NumPy vectorization instead of a loop"
        - "Detected memory leak at line 89: Ensure file handles are closed"
        - "High CPU usage at line 123: Cache the result instead of recomputing"
        - "Memory-intensive operation at line 67: Use a generator instead of building a list"

    Example:
        Get optimization advice:
        recommendations = get_recommendations(profile_id)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
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
    """
    Get function-level performance summary showing resource usage per function.

    Use this for a higher-level view than line-by-line analysis. Shows which functions (not lines)
    are consuming resources, aggregating all lines within each function. Useful for identifying
    which components or modules are expensive.

    **When to use**: When you want to see which functions/methods are slowest, not individual lines.
    **Returns**: List of functions ranked by CPU usage, with aggregated time and memory metrics.

    Args:
        profile_id: ID returned from profile_script or profile_code
        top_n: Maximum number of functions to return (e.g., top 10 most expensive functions)

    Returns:
        List of dictionaries, each containing:
        - function_name: Name of the function or method
        - filename: File containing the function
        - start_line: First line of the function
        - total_cpu_percent: Total CPU time spent in this function (sum of all lines)
        - total_memory_mb: Total memory allocated by this function
        - call_count: How many times this function was called (if available)

    Example:
        Find most expensive functions:
        functions = get_function_summary(profile_id, top_n=5)
        for func in functions:
            print(f"{func['function_name']} used {func['total_cpu_percent']:.1f}% CPU")
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

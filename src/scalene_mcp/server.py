"""Scalene MCP Server.

Main FastMCP server with tools, resources, and prompts for Scalene profiling.
"""

from fastmcp import FastMCP

# Create the MCP server
server = FastMCP("Scalene Profiler")


@server.tool
async def profile(
    script_path: str | None = None,
    code: str | None = None,
) -> dict[str, str]:
    """
    Profile Python code with Scalene.

    Provide either script_path or code. Returns a profile ID and summary.

    Args:
        script_path: Path to Python script to profile
        code: Python code snippet to profile

    Returns:
        Dictionary with profile_id and summary
    """
    if script_path is None and code is None:
        raise ValueError("Must provide either script_path or code")

    if script_path and code:
        raise ValueError("Provide only one of script_path or code")

    # Placeholder implementation
    return {
        "profile_id": "profile_001",
        "summary": "Profiling completed successfully (placeholder)",
    }


def main() -> None:
    """Entry point for running the server."""
    server.run()


if __name__ == "__main__":
    main()

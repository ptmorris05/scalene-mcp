"""Basic smoke tests for MCP server."""

import pytest
from fastmcp import FastMCP


@pytest.mark.asyncio
async def test_server_initializes(server: FastMCP) -> None:
    """Test that the MCP server initializes correctly."""
    assert server is not None
    assert server.name == "Scalene Profiler"


@pytest.mark.asyncio
async def test_list_tools(server: FastMCP) -> None:
    """Test that tools are registered."""
    tools = server.list_tools()
    tool_names = {tool.name for tool in tools}

    # Should have at least the profile tool
    assert "profile" in tool_names


@pytest.mark.asyncio
async def test_profile_tool_basic(server: FastMCP) -> None:
    """Test basic profile tool invocation."""
    result = await server.call_tool(
        "profile",
        arguments={"code": "print('hello')"},
    )

    assert result is not None

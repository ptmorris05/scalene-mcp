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
    tools = await server.get_tools()
    # In FastMCP 2.14.3, get_tools() returns a dict
    tool_names = set(tools.keys())

    # Should have at least the profile tool
    assert "profile" in tool_names


@pytest.mark.asyncio
async def test_profile_tool_exists(server: FastMCP) -> None:
    """Test that profile tool is registered with correct metadata."""
    tools = await server.get_tools()
    
    assert "profile" in tools
    tool = tools["profile"]
    assert tool.name == "profile"
    assert "Profile Python code with Scalene" in tool.description
    
    # Check that the tool has the expected parameters
    mcp_tool = tool.to_mcp_tool()
    schema_str = str(mcp_tool.inputSchema)
    assert "script_path" in schema_str
    assert "code" in schema_str

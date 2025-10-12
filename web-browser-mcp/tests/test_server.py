"""Tests for the MCP Web Browser server."""

import pytest
from mcp_web_browser.server import main_mcp


def test_server_creation():
    """Test that the MCP server is created properly."""
    assert main_mcp.name == "Web Browser"
    assert "web browsing" in main_mcp.description.lower()


def test_tools_exist():
    """Test that the expected tools are registered."""
    tools = main_mcp.list_tools()
    tool_names = [tool.name for tool in tools]

    assert "browse_url" in tool_names
    assert "get_page_title" in tool_names


@pytest.mark.asyncio
async def test_browse_url_tool():
    """Test the browse_url tool (mocked)."""
    # This would need mocking for actual browser testing
    # For now, just test that the tool exists and can be called
    tools = main_mcp.list_tools()
    browse_tool = next((t for t in tools if t.name == "browse_url"), None)
    assert browse_tool is not None
    assert "url" in browse_tool.inputSchema["properties"]


@pytest.mark.asyncio
async def test_get_page_title_tool():
    """Test the get_page_title tool (mocked)."""
    tools = main_mcp.list_tools()
    title_tool = next((t for t in tools if t.name == "get_page_title"), None)
    assert title_tool is not None
    assert "url" in title_tool.inputSchema["properties"]
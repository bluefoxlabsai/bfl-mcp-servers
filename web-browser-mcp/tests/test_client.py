"""Test client for MCP Web Browser."""

import asyncio
import json
from typing import Any, Dict

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_web_browser.server import main_mcp


@pytest.mark.asyncio
async def test_client_connection():
    """Test that a client can connect to the server."""
    # Start the server in a separate task
    server_task = asyncio.create_task(main_mcp.run_async())

    # Give the server a moment to start
    await asyncio.sleep(0.1)

    try:
        # Create client
        async with stdio_client(StdioServerParameters(command="python", args=["-m", "mcp_web_browser"])) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                # List tools
                tools = await session.list_tools()
                tool_names = [tool.name for tool in tools]

                assert "browse_url" in tool_names
                assert "get_page_title" in tool_names

    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
"""Example script to demonstrate HTTP transport with the Slack MCP Server."""

import asyncio
import json
import os
import subprocess
import sys
import time
import aiohttp
from typing import Any, Dict

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get and validate environment variables
slack_token = os.getenv("EXAMPLES_SLACK_BOT_TOKEN")
user_token = os.getenv("EXAMPLES_SLACK_USER_TOKEN")

if not slack_token:
    raise ValueError("EXAMPLES_SLACK_BOT_TOKEN environment variable is required")

if not user_token:
    raise ValueError("EXAMPLES_SLACK_USER_TOKEN environment variable is required")


class MCPHttpClient:
    """HTTP client for MCP server."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool via HTTP."""
        
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        async with self.session.post(
            f"{self.base_url}/mcp",
            json=mcp_request,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"HTTP request failed with status {response.status}")


async def start_server(port: int = 3000):
    """Start the MCP server in HTTP mode."""
    
    env = os.environ.copy()
    env["SLACK_BOT_TOKEN"] = slack_token
    env["SLACK_USER_TOKEN"] = user_token
    
    process = subprocess.Popen(
        [sys.executable, "-m", "slack_mcp_server.server", "--port", str(port)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    await asyncio.sleep(2)
    
    return process


async def main():
    """Main function to demonstrate HTTP transport."""
    
    print("🚀 Starting Slack MCP Server HTTP example...")
    print("=" * 50)
    
    port = 3000
    server_process = None
    
    try:
        # Start the server
        print(f"🌐 Starting MCP server on port {port}...")
        server_process = await start_server(port)
        
        # Give server time to fully start
        await asyncio.sleep(3)
        
        # Test HTTP connection
        base_url = f"http://localhost:{port}"
        
        async with MCPHttpClient(base_url) as client:
            print("📋 Calling slack_get_users tool via HTTP...")
            
            response = await client.call_tool("slack_get_users", {"limit": 5})
            
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    result_text = content[0].get("text", "")
                    try:
                        users_data = json.loads(result_text)
                        print(f"✅ Successfully retrieved users via HTTP!")
                        print(f"📊 Response metadata:")
                        print(f"   - OK: {users_data.get('ok', False)}")
                        
                        members = users_data.get('members', [])
                        print(f"   - Total members returned: {len(members)}")
                        
                        if members:
                            print("\n👥 Users list (via HTTP):")
                            print("-" * 30)
                            
                            for i, member in enumerate(members[:3], 1):  # Show first 3 users
                                name = member.get('name', 'N/A')
                                real_name = member.get('real_name', 'N/A')
                                is_bot = member.get('is_bot', False)
                                
                                print(f"{i}. {name}")
                                print(f"   Real name: {real_name}")
                                print(f"   Is bot: {is_bot}")
                                print()
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse users data: {e}")
                else:
                    print("❌ No content in HTTP response")
            else:
                print(f"❌ Unexpected HTTP response format: {response}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up server process
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
    
    print("\n" + "=" * 50)
    print("🏁 HTTP example completed!")


if __name__ == "__main__":
    asyncio.run(main())
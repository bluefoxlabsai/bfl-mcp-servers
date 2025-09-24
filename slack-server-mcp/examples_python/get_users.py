"""Example script to demonstrate getting users from the Slack MCP Server."""

import asyncio
import json
import os
import subprocess
import sys
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


async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call an MCP tool via subprocess."""
    
    # Prepare the environment for the subprocess
    env = os.environ.copy()
    env["SLACK_BOT_TOKEN"] = slack_token
    env["SLACK_USER_TOKEN"] = user_token
    
    # Start the MCP server process
    process = subprocess.Popen(
        [sys.executable, "-m", "slack_mcp_server.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    # Prepare MCP request
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        # Send request to the server
        stdout, stderr = process.communicate(
            input=json.dumps(mcp_request) + "\n",
            timeout=30
        )
        
        # Parse the response
        if process.returncode == 0 and stdout.strip():
            lines = stdout.strip().split('\n')
            for line in lines:
                try:
                    response = json.loads(line)
                    if response.get("id") == 1:
                        return response
                except json.JSONDecodeError:
                    continue
        
        raise Exception(f"MCP call failed. Return code: {process.returncode}, stderr: {stderr}")
        
    except subprocess.TimeoutExpired:
        process.kill()
        raise Exception("MCP call timed out")
    finally:
        if process.poll() is None:
            process.terminate()


async def main():
    """Main function to demonstrate getting users."""
    
    print("🚀 Starting Slack MCP Server get_users example...")
    print("=" * 50)
    
    try:
        # Call the slack_get_users tool
        print("📋 Calling slack_get_users tool...")
        response = await call_mcp_tool("slack_get_users", {"limit": 10})
        
        if "result" in response and "content" in response["result"]:
            # Parse the result content
            content = response["result"]["content"]
            if isinstance(content, list) and len(content) > 0:
                result_text = content[0].get("text", "")
                try:
                    users_data = json.loads(result_text)
                    print(f"✅ Successfully retrieved users!")
                    print(f"📊 Response metadata:")
                    print(f"   - OK: {users_data.get('ok', False)}")
                    
                    members = users_data.get('members', [])
                    print(f"   - Total members returned: {len(members)}")
                    
                    if members:
                        print("\n👥 Users list:")
                        print("-" * 30)
                        
                        for i, member in enumerate(members[:5], 1):  # Show first 5 users
                            name = member.get('name', 'N/A')
                            real_name = member.get('real_name', 'N/A')
                            is_bot = member.get('is_bot', False)
                            is_deleted = member.get('deleted', False)
                            
                            print(f"{i}. {name}")
                            print(f"   Real name: {real_name}")
                            print(f"   Is bot: {is_bot}")
                            print(f"   Is deleted: {is_deleted}")
                            print()
                        
                        if len(members) > 5:
                            print(f"... and {len(members) - 5} more users")
                    
                    # Check for pagination
                    response_metadata = users_data.get('response_metadata', {})
                    if response_metadata.get('next_cursor'):
                        print(f"\n📄 More users available (next_cursor: {response_metadata['next_cursor'][:20]}...)")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse users data: {e}")
                    print(f"Raw response: {result_text[:200]}...")
            else:
                print("❌ No content in response")
        else:
            print(f"❌ Unexpected response format: {response}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Example completed!")


if __name__ == "__main__":
    asyncio.run(main())
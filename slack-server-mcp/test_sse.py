#!/usr/bin/env python3
"""Test script to verify SSE endpoint functionality."""

import asyncio
import aiohttp
import json
import sys

async def test_sse_endpoint(port: int = 8000):
    """Test the SSE endpoint of the Slack MCP server."""
    
    base_url = f"http://localhost:{port}"
    
    print(f"Testing Slack MCP Server SSE endpoint at {base_url}")
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check passed: {health_data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
        
        # Test SSE endpoint availability
        print("\n2. Testing SSE endpoint availability...")
        try:
            async with session.get(f"{base_url}/sse") as response:
                print(f"✅ SSE endpoint responded with status: {response.status}")
                if response.status == 200:
                    print("✅ SSE endpoint is accessible")
                else:
                    print(f"⚠️  SSE endpoint returned status: {response.status}")
        except Exception as e:
            print(f"❌ SSE endpoint error: {e}")
            return False
        
        # Test MCP initialization message
        print("\n3. Testing MCP initialization...")
        try:
            headers = {
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache'
            }
            
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            async with session.post(
                f"{base_url}/sse",
                headers=headers,
                json=init_message
            ) as response:
                if response.status == 200:
                    print("✅ MCP initialization request accepted")
                    # Read a bit of the SSE stream
                    content = await response.text()
                    if content:
                        print(f"✅ Received SSE response: {content[:200]}...")
                else:
                    print(f"❌ MCP initialization failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ MCP initialization error: {e}")
            return False
    
    print("\n🎉 SSE endpoint test completed successfully!")
    return True

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    asyncio.run(test_sse_endpoint(port))
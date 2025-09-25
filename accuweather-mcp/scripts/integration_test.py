#!/usr/bin/env python3
"""Integration test for AccuWeather MCP server with SSE transport."""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

import httpx

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def test_sse_server(port: int = 8000, timeout: int = 30) -> bool:
    """Test the SSE server functionality."""
    
    base_url = f"http://localhost:{port}"
    
    print(f"🔍 Testing SSE server at {base_url}")
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            # Test 1: Health check
            print("❤️  Testing health endpoint...")
            health_response = await client.get(f"{base_url}/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Health check passed: {health_data}")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                return False
            
            # Test 2: SSE endpoint availability
            print("📡 Testing SSE endpoint...")
            sse_response = await client.get(f"{base_url}/sse")
            if sse_response.status_code == 200:
                print("✅ SSE endpoint is accessible")
            else:
                print(f"❌ SSE endpoint failed: {sse_response.status_code}")
                return False
            
            return True
            
        except httpx.ConnectError:
            print(f"❌ Cannot connect to server at {base_url}")
            print("   Make sure the server is running with: uv run mcp-accuweather --port 8000")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False


async def test_mcp_tools_via_sse(port: int = 8000) -> bool:
    """Test MCP tools through SSE interface."""
    
    print("🔧 Testing MCP tools via SSE...")
    
    # This would require implementing an MCP client to test the actual tools
    # For now, we'll just verify the server structure
    
    try:
        from mcp_accuweather.server import create_server
        
        server = create_server()
        tools = server.list_tools()
        
        expected_tools = [
            "search_locations",
            "get_current_conditions", 
            "get_5day_forecast",
            "get_hourly_forecast",
            "get_weather_alerts",
            "get_historical_weather",
            "get_location_key"
        ]
        
        tool_names = [tool.name for tool in tools]
        
        print(f"📋 Available tools: {len(tool_names)}")
        for name in tool_names:
            print(f"   ✅ {name}")
        
        missing_tools = set(expected_tools) - set(tool_names)
        if missing_tools:
            print(f"❌ Missing tools: {missing_tools}")
            return False
        
        print("✅ All expected tools are available")
        return True
        
    except Exception as e:
        print(f"❌ Error testing MCP tools: {e}")
        return False


def check_environment() -> bool:
    """Check if the environment is properly configured."""
    
    print("🔍 Checking environment configuration...")
    
    # Check for API key
    api_key = os.getenv("ACCUWEATHER_API_KEY")
    if not api_key:
        print("❌ ACCUWEATHER_API_KEY environment variable is required")
        
        # Check .env file
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            print(f"📁 Found .env file at {env_file}")
            with open(env_file) as f:
                content = f.read()
                if "ACCUWEATHER_API_KEY=" in content:
                    print("⚠️  API key is set in .env file but not loaded")
                    print("   Try: source .env or use python-dotenv")
                else:
                    print("❌ API key not found in .env file")
        else:
            print("❌ No .env file found")
        
        return False
    
    print(f"✅ API key found: {api_key[:8]}...")
    
    # Check dependencies
    try:
        import mcp_accuweather
        print("✅ mcp_accuweather module is available")
    except ImportError as e:
        print(f"❌ Cannot import mcp_accuweather: {e}")
        print("   Try: uv sync")
        return False
    
    return True


async def run_full_integration_test(port: int = 8000) -> bool:
    """Run the complete integration test suite."""
    
    print("🧪 AccuWeather MCP Integration Test Suite")
    print("=" * 60)
    
    # Step 1: Environment check
    if not check_environment():
        return False
    
    # Step 2: Test server endpoints
    server_ok = await test_sse_server(port)
    if not server_ok:
        return False
    
    # Step 3: Test MCP tools
    tools_ok = await test_mcp_tools_via_sse(port)
    if not tools_ok:
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All integration tests passed!")
    print(f"🌐 Server is running at http://localhost:{port}")
    print(f"📡 SSE endpoint: http://localhost:{port}/sse")
    print(f"❤️  Health check: http://localhost:{port}/health")
    
    return True


def main():
    """Main test function."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="AccuWeather MCP Integration Test")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--env-only", action="store_true", help="Only check environment")
    
    args = parser.parse_args()
    
    # Load environment variables from .env file if it exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            print("⚠️  python-dotenv not available, .env file not loaded")
    
    if args.env_only:
        success = check_environment()
    else:
        success = asyncio.run(run_full_integration_test(args.port))
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
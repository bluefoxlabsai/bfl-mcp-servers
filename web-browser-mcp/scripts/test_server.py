#!/usr/bin/env python3

"""
Test script for Web Browser MCP server.

This script tests the MCP server by making HTTP requests to the running server.
"""

import requests
import json
import sys
from typing import Dict, Any

def test_health_check(base_url: str = "http://localhost:8000") -> bool:
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_mcp_tools(base_url: str = "http://localhost:8000") -> bool:
    """Test listing MCP tools."""
    try:
        # MCP protocol for listing tools
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }

        response = requests.post(f"{base_url}/mcp", json=payload)
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                tool_names = [tool["name"] for tool in tools]
                print(f"✅ Found tools: {', '.join(tool_names)}")
                expected_tools = ["browse_url", "get_page_title"]
                if all(tool in tool_names for tool in expected_tools):
                    print("✅ All expected tools present")
                    return True
                else:
                    print(f"❌ Missing tools. Expected: {expected_tools}, Found: {tool_names}")
                    return False
            else:
                print("❌ Invalid response format")
                return False
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tools list error: {e}")
        return False

def main():
    """Main test function."""
    base_url = "http://localhost:8000"

    print("🧪 Testing Web Browser MCP Server")
    print(f"Server URL: {base_url}")
    print()

    tests = [
        ("Health Check", test_health_check),
        ("MCP Tools", test_mcp_tools),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        if test_func(base_url):
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
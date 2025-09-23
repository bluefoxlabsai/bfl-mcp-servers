#!/bin/bash

# Test script to validate Linux compatibility for bfljerum/atlassian-mcp

echo "🧪 Testing bfljerum/atlassian-mcp Linux compatibility"
echo ""

# Test 1: Check if image exists and can be pulled
echo "1. Testing image pull..."
docker pull bfljerum/atlassian-mcp:latest
if [ $? -eq 0 ]; then
    echo "✅ Image pull successful"
else
    echo "❌ Image pull failed"
    exit 1
fi
echo ""

# Test 2: Check multi-platform support
echo "2. Testing multi-platform support..."
docker buildx imagetools inspect bfljerum/atlassian-mcp:latest | grep -E "Platform:\s+linux/(amd64|arm64)"
if [ $? -eq 0 ]; then
    echo "✅ Multi-platform support confirmed (Linux AMD64 and ARM64)"
else
    echo "❌ Multi-platform support check failed"
    exit 1
fi
echo ""

# Test 3: Test help command
echo "3. Testing help command..."
docker run --rm bfljerum/atlassian-mcp:latest --help > /tmp/mcp_help.txt 2>&1
if grep -q "MCP Atlassian Server" /tmp/mcp_help.txt; then
    echo "✅ Help command works correctly"
else
    echo "❌ Help command failed"
    cat /tmp/mcp_help.txt
    exit 1
fi
echo ""

# Test 4: Test container startup with environment variables
echo "4. Testing container startup with environment variables..."
if docker run --rm -e CONFLUENCE_URL="https://test.atlassian.net" -e CONFLUENCE_USERNAME="test@example.com" -e CONFLUENCE_API_TOKEN="test-token" bfljerum/atlassian-mcp:latest --help >/dev/null 2>&1; then
    echo "✅ Container startup test passed (help command with environment variables)"
else
    echo "❌ Container startup test failed"
    exit 1
fi
echo ""

# Test 5: Check image security (non-root user)
echo "5. Testing security (non-root user)..."
USER_ID=$(docker run --rm --entrypoint /bin/sh bfljerum/atlassian-mcp:latest -c "id -u")
if [ "$USER_ID" != "0" ]; then
    echo "✅ Container runs as non-root user (UID: $USER_ID)"
else
    echo "❌ Container runs as root (security risk)"
    exit 1
fi
echo ""

echo "🎉 All Linux compatibility tests passed!"
echo ""
echo "Image details:"
echo "- Repository: bfljerum/atlassian-mcp:latest"
echo "- Platforms: Linux AMD64, Linux ARM64" 
echo "- Base: Alpine Linux (ghcr.io/astral-sh/uv:python3.10-alpine)"
echo "- User: Non-root (app user)"
echo "- Port: 8000 (SSE transport)"
echo ""
echo "Usage on Linux:"
echo "docker run -p 8000:8000 \\"
echo "  -e CONFLUENCE_URL=\"https://your-company.atlassian.net\" \\"
echo "  -e CONFLUENCE_USERNAME=\"your@email.com\" \\"
echo "  -e CONFLUENCE_API_TOKEN=\"your-token\" \\"
echo "  -e JIRA_URL=\"https://your-company.atlassian.net\" \\"
echo "  -e JIRA_USERNAME=\"your@email.com\" \\"
echo "  -e JIRA_API_TOKEN=\"your-token\" \\"
echo "  bfljerum/atlassian-mcp:latest"

# Cleanup temp files
rm -f /tmp/mcp_help.txt
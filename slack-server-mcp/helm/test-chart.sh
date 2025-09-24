#!/bin/bash

# Test script for Slack MCP Server Helm Chart
# This script validates the Helm chart templates and configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_color() {
    printf "${1}${2}${NC}\n"
}

print_color $BLUE "🧪 Testing Slack MCP Server Helm Chart"
echo ""

# Check if helm is available
if ! command -v helm &> /dev/null; then
    print_color $RED "❌ Helm is not installed"
    exit 1
fi

print_color $YELLOW "📋 Running Helm chart tests..."

# Test 1: Lint the chart
print_color $BLUE "1. Linting Helm chart..."
if helm lint .; then
    print_color $GREEN "✅ Helm lint passed"
else
    print_color $RED "❌ Helm lint failed"
    exit 1
fi

# Test 2: Template rendering with SSE transport
print_color $BLUE "2. Testing SSE transport template rendering..."
if helm template test-sse . \
    --set mcp.transport=sse \
    --set slack.botToken=xoxb-test \
    --set slack.userToken=xoxp-test \
    > /dev/null; then
    print_color $GREEN "✅ SSE transport template rendering passed"
else
    print_color $RED "❌ SSE transport template rendering failed"
    exit 1
fi

# Test 3: Template rendering with STDIO transport
print_color $BLUE "3. Testing STDIO transport template rendering..."
if helm template test-stdio . \
    --set mcp.transport=stdio \
    --set slack.botToken=xoxb-test \
    --set slack.userToken=xoxp-test \
    > /dev/null; then
    print_color $GREEN "✅ STDIO transport template rendering passed"
else
    print_color $RED "❌ STDIO transport template rendering failed"
    exit 1
fi

# Test 4: Template rendering with HTTP transport
print_color $BLUE "4. Testing HTTP transport template rendering..."
if helm template test-http . \
    --set mcp.transport=http \
    --set slack.botToken=xoxb-test \
    --set slack.userToken=xoxp-test \
    > /dev/null; then
    print_color $GREEN "✅ HTTP transport template rendering passed"
else
    print_color $RED "❌ HTTP transport template rendering failed"
    exit 1
fi

# Test 5: Validate service is enabled for SSE
print_color $BLUE "5. Validating service configuration for SSE transport..."
SERVICE_OUTPUT=$(helm template test-sse . \
    --set mcp.transport=sse \
    --set slack.botToken=xoxb-test \
    --set slack.userToken=xoxp-test \
    | grep -A 10 "kind: Service" || true)

if [[ -n "$SERVICE_OUTPUT" ]]; then
    print_color $GREEN "✅ Service is correctly enabled for SSE transport"
else
    print_color $RED "❌ Service is not enabled for SSE transport"
    exit 1
fi

# Test 6: Validate service is disabled for STDIO
print_color $BLUE "6. Validating service configuration for STDIO transport..."
SERVICE_COUNT=$(helm template test-stdio . \
    --set mcp.transport=stdio \
    --set slack.botToken=xoxb-test \
    --set slack.userToken=xoxp-test \
    | grep -c "^kind: Service$" || true)

if [[ "$SERVICE_COUNT" -eq "0" ]]; then
    print_color $GREEN "✅ Service is correctly disabled for STDIO transport"
else
    print_color $RED "❌ Service should be disabled for STDIO transport (found $SERVICE_COUNT services)"
    exit 1
fi

# Test 7: Validate probes are enabled for SSE
print_color $BLUE "7. Validating health probes for SSE transport..."
PROBE_OUTPUT=$(helm template test-sse . \
    --set mcp.transport=sse \
    --set slack.botToken=xoxb-test \
    --set slack.userToken=xoxp-test \
    | grep -A 5 "livenessProbe\|readinessProbe" || true)

if [[ -n "$PROBE_OUTPUT" ]]; then
    print_color $GREEN "✅ Health probes are correctly enabled for SSE transport"
else
    print_color $RED "❌ Health probes are not enabled for SSE transport"
    exit 1
fi

# Test 8: Validate example values files
print_color $BLUE "8. Testing example values files..."
for example_file in examples/*.example; do
    if [[ -f "$example_file" ]]; then
        filename=$(basename "$example_file")
        print_color $YELLOW "   Testing $filename..."
        if helm template test-example . -f "$example_file" \
            --set slack.botToken=xoxb-test \
            --set slack.userToken=xoxp-test \
            > /dev/null; then
            print_color $GREEN "   ✅ $filename passed"
        else
            print_color $RED "   ❌ $filename failed"
            exit 1
        fi
    fi
done

echo ""
print_color $GREEN "🎉 All Helm chart tests passed!"
print_color $BLUE "📋 Chart is ready for deployment with SSE transport support"

echo ""
print_color $YELLOW "💡 Quick deployment commands:"
echo "   # SSE transport (recommended for Kubernetes)"
echo "   helm install slack-mcp . --set mcp.transport=sse --set slack.botToken=xoxb-xxx --set slack.userToken=xoxp-xxx"
echo ""
echo "   # STDIO transport (for direct MCP clients)"
echo "   helm install slack-mcp . --set mcp.transport=stdio --set slack.botToken=xoxb-xxx --set slack.userToken=xoxp-xxx"
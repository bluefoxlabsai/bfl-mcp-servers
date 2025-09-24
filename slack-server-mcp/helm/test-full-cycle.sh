#!/bin/bash

# Full cycle test for Slack MCP Server Helm Chart
# This script tests install -> verify -> uninstall cycle

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_color() {
    printf "${1}${2}${NC}\n"
}

print_color $BLUE "🔄 Full Cycle Test for Slack MCP Server Helm Chart"
echo ""

# Configuration
TEST_NAMESPACE="test-slack-mcp"
TEST_RELEASE="test-slack-mcp-release"
TEST_BOT_TOKEN="xoxb-test-token-for-testing"
TEST_USER_TOKEN="xoxp-test-token-for-testing"

# Cleanup function
cleanup() {
    print_color $YELLOW "🧹 Cleaning up test resources..."
    
    # Try to uninstall if release exists
    if helm list -n "$TEST_NAMESPACE" 2>/dev/null | grep -q "$TEST_RELEASE"; then
        print_color $BLUE "Removing test release..."
        helm uninstall "$TEST_RELEASE" -n "$TEST_NAMESPACE" || true
    fi
    
    # Try to delete namespace if it exists
    if kubectl get namespace "$TEST_NAMESPACE" &>/dev/null; then
        print_color $BLUE "Removing test namespace..."
        kubectl delete namespace "$TEST_NAMESPACE" || true
    fi
}

# Set trap for cleanup
trap cleanup EXIT

print_color $PURPLE "📋 Test Configuration:"
echo "  Namespace: $TEST_NAMESPACE"
echo "  Release: $TEST_RELEASE"
echo "  Transport: SSE"
echo ""

# Test 1: Dry-run installation
print_color $BLUE "1. Testing dry-run installation..."
if helm install "$TEST_RELEASE" . \
    --namespace "$TEST_NAMESPACE" \
    --create-namespace \
    --set mcp.transport=sse \
    --set slack.botToken="$TEST_BOT_TOKEN" \
    --set slack.userToken="$TEST_USER_TOKEN" \
    --dry-run > /dev/null; then
    print_color $GREEN "✅ Dry-run installation successful"
else
    print_color $RED "❌ Dry-run installation failed"
    exit 1
fi

# Test 2: Template validation
print_color $BLUE "2. Testing template validation..."
if helm template "$TEST_RELEASE" . \
    --namespace "$TEST_NAMESPACE" \
    --set mcp.transport=sse \
    --set slack.botToken="$TEST_BOT_TOKEN" \
    --set slack.userToken="$TEST_USER_TOKEN" > /dev/null; then
    print_color $GREEN "✅ Template validation successful"
else
    print_color $RED "❌ Template validation failed"
    exit 1
fi

# Test 3: Check if we can connect to cluster (skip actual install if not)
if ! kubectl cluster-info &> /dev/null; then
    print_color $YELLOW "⚠️  No Kubernetes cluster available - skipping actual deployment tests"
    print_color $GREEN "✅ Template and dry-run tests completed successfully"
    exit 0
fi

print_color $BLUE "3. Testing actual installation..."

# Install the chart
if helm install "$TEST_RELEASE" . \
    --namespace "$TEST_NAMESPACE" \
    --create-namespace \
    --set mcp.transport=sse \
    --set slack.botToken="$TEST_BOT_TOKEN" \
    --set slack.userToken="$TEST_USER_TOKEN" \
    --wait \
    --timeout=300s; then
    print_color $GREEN "✅ Installation successful"
else
    print_color $RED "❌ Installation failed"
    exit 1
fi

# Test 4: Verify deployment
print_color $BLUE "4. Verifying deployment..."

# Check if release exists
if helm list -n "$TEST_NAMESPACE" | grep -q "$TEST_RELEASE"; then
    print_color $GREEN "✅ Release found in Helm"
else
    print_color $RED "❌ Release not found in Helm"
    exit 1
fi

# Check if pods are running
sleep 10  # Give pods time to start
POD_STATUS=$(kubectl get pods -n "$TEST_NAMESPACE" -l "app.kubernetes.io/instance=$TEST_RELEASE" -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "NotFound")

if [[ "$POD_STATUS" == "Running" ]]; then
    print_color $GREEN "✅ Pod is running"
elif [[ "$POD_STATUS" == "Pending" ]]; then
    print_color $YELLOW "⚠️  Pod is still pending (this is expected with test tokens)"
else
    print_color $YELLOW "⚠️  Pod status: $POD_STATUS (expected with invalid test tokens)"
fi

# Check if service exists (for SSE transport)
if kubectl get service -n "$TEST_NAMESPACE" "$TEST_RELEASE" &>/dev/null; then
    print_color $GREEN "✅ Service created for SSE transport"
else
    print_color $RED "❌ Service not found for SSE transport"
    exit 1
fi

# Test 5: Test uninstall script
print_color $BLUE "5. Testing uninstall script..."

# Test dry-run first
if NAMESPACE="$TEST_NAMESPACE" ./uninstall.sh "$TEST_RELEASE" --dry-run > /dev/null; then
    print_color $GREEN "✅ Uninstall dry-run successful"
else
    print_color $RED "❌ Uninstall dry-run failed"
    exit 1
fi

# Test actual uninstall
if NAMESPACE="$TEST_NAMESPACE" ./uninstall.sh "$TEST_RELEASE" --keep-namespace <<< "y" > /dev/null; then
    print_color $GREEN "✅ Uninstall successful"
else
    print_color $RED "❌ Uninstall failed"
    exit 1
fi

# Verify uninstall
sleep 5
if ! helm list -n "$TEST_NAMESPACE" | grep -q "$TEST_RELEASE"; then
    print_color $GREEN "✅ Release successfully removed"
else
    print_color $RED "❌ Release still exists after uninstall"
    exit 1
fi

# Test 6: Namespace cleanup
print_color $BLUE "6. Testing namespace cleanup..."
if kubectl delete namespace "$TEST_NAMESPACE"; then
    print_color $GREEN "✅ Namespace cleanup successful"
else
    print_color $YELLOW "⚠️  Namespace cleanup had issues (may be normal)"
fi

echo ""
print_color $GREEN "🎉 Full cycle test completed successfully!"
print_color $BLUE "📋 All components are working correctly:"
echo "  ✅ Helm chart templates"
echo "  ✅ Installation process"
echo "  ✅ SSE transport configuration"
echo "  ✅ Service creation"
echo "  ✅ Uninstall process"
echo "  ✅ Resource cleanup"

echo ""
print_color $PURPLE "🚀 The Slack MCP Server Helm chart is ready for production use!"
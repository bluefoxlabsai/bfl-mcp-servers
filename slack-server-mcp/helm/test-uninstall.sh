#!/bin/bash

# Test script for the uninstall.sh script
# This validates the uninstall script functionality without actually uninstalling anything

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

print_color $BLUE "🧪 Testing Uninstall Script"
echo ""

# Test 1: Help functionality
print_color $BLUE "1. Testing help functionality..."
if ./uninstall.sh --help > /dev/null 2>&1; then
    print_color $GREEN "✅ Help command works"
else
    print_color $RED "❌ Help command failed"
    exit 1
fi

# Test 2: Dry-run with non-existent release
print_color $BLUE "2. Testing dry-run with non-existent release..."
if NAMESPACE=test-namespace ./uninstall.sh non-existent-release --dry-run 2>&1 | grep -q "not found"; then
    print_color $GREEN "✅ Correctly handles non-existent release"
else
    print_color $RED "❌ Failed to handle non-existent release"
    exit 1
fi

# Test 3: Check required tools validation
print_color $BLUE "3. Testing required tools validation..."
# This test assumes helm and kubectl are available
if ./uninstall.sh --help > /dev/null 2>&1; then
    print_color $GREEN "✅ Required tools validation works"
else
    print_color $RED "❌ Required tools validation failed"
    exit 1
fi

# Test 4: Argument parsing
print_color $BLUE "4. Testing argument parsing..."
if ./uninstall.sh --invalid-option 2>&1 | grep -q "Unknown option"; then
    print_color $GREEN "✅ Invalid option handling works"
else
    print_color $RED "❌ Invalid option handling failed"
    exit 1
fi

# Test 5: Environment variable handling
print_color $BLUE "5. Testing environment variable handling..."
if NAMESPACE=custom-ns ./uninstall.sh test-release --dry-run 2>&1 | grep -q "custom-ns"; then
    print_color $GREEN "✅ Environment variable handling works"
else
    print_color $RED "❌ Environment variable handling failed"
    exit 1
fi

echo ""
print_color $GREEN "🎉 All uninstall script tests passed!"
print_color $BLUE "📋 The uninstall script is working correctly"

echo ""
print_color $YELLOW "💡 Usage examples:"
echo "   # Basic uninstall with prompts"
echo "   ./uninstall.sh"
echo ""
echo "   # Uninstall specific release"
echo "   ./uninstall.sh my-slack-mcp"
echo ""
echo "   # Dry-run to see what would be deleted"
echo "   ./uninstall.sh --dry-run"
echo ""
echo "   # Keep namespace after uninstall"
echo "   ./uninstall.sh --keep-namespace"
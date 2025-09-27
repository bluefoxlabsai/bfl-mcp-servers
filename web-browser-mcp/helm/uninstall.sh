#!/bin/bash

# Web Browser MCP Helm Chart Uninstallation Script
#
# Usage:
#   ./uninstall.sh [release-name]
#
# Environment Variables:
#   NAMESPACE - Kubernetes namespace (optional, defaults to 'default')
#
# Examples:
#   ./uninstall.sh                    # Uninstall with default release name
#   ./uninstall.sh my-web-browser-mcp # Uninstall with custom release name
#   NAMESPACE=web ./uninstall.sh      # Uninstall from 'web' namespace

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

print_color $BLUE "🗑️  Web Browser MCP Helm Chart Uninstaller"
echo ""

# Default values
RELEASE_NAME=${1:-"web-browser-mcp"}
NAMESPACE=${NAMESPACE:-"mcp-servers"}

print_color $YELLOW "Configuration:"
echo "  Release Name: $RELEASE_NAME"
echo "  Namespace: $NAMESPACE"
echo ""

# Confirm uninstallation
read -p "Are you sure you want to uninstall $RELEASE_NAME from namespace $NAMESPACE? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_color $YELLOW "Uninstallation cancelled."
    exit 0
fi

# Uninstall the Helm chart
print_color $BLUE "Uninstalling Helm chart..."
helm uninstall "$RELEASE_NAME" --namespace "$NAMESPACE"

print_color $GREEN "✅ Uninstallation completed successfully!"

# Optionally clean up namespace
read -p "Do you want to delete the namespace $NAMESPACE? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_color $YELLOW "Deleting namespace: $NAMESPACE"
    kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
    print_color $GREEN "Namespace deleted."
fi

print_color $GREEN "🎉 Cleanup completed!"
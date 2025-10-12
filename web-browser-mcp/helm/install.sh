#!/bin/bash

# Web Browser MCP Helm Chart Installation Script
#
# Usage:
#   ./install.sh [release-name]
#
# Environment Variables:
#   NAMESPACE - Kubernetes namespace (optional, defaults to 'default')
#
# Examples:
#   ./install.sh                              # Install with default release name
#   ./install.sh my-web-browser-mcp           # Install with custom release name
#   NAMESPACE=web ./install.sh                # Install in 'web' namespace

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

print_color $BLUE "🚀 Web Browser MCP Helm Chart Installer"
echo ""

# Default values
RELEASE_NAME=${1:-"web-browser-mcp"}
NAMESPACE=${NAMESPACE:-"mcp-servers"}

print_color $YELLOW "Configuration:"
echo "  Release Name: $RELEASE_NAME"
echo "  Namespace: $NAMESPACE"
echo ""

# Check if namespace exists, create if not
if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    print_color $YELLOW "Creating namespace: $NAMESPACE"
    kubectl create namespace "$NAMESPACE"
fi

# Install the Helm chart
print_color $BLUE "Installing Helm chart..."
helm upgrade --install "$RELEASE_NAME" . \
    --namespace "$NAMESPACE" \
    --wait

print_color $GREEN "✅ Installation completed successfully!"
echo ""

# Get service information
SERVICE_NAME="$RELEASE_NAME-web-browser-mcp"
if kubectl get svc "$SERVICE_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
    print_color $BLUE "Service Information:"
    kubectl get svc "$SERVICE_NAME" -n "$NAMESPACE"
    echo ""
    print_color $YELLOW "To port-forward and test:"
    echo "  kubectl port-forward svc/$SERVICE_NAME -n $NAMESPACE 8000:8000"
    echo "  curl http://localhost:8000/health"
fi

print_color $GREEN "🎉 Web Browser MCP is ready!"
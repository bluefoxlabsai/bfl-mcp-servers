#!/bin/bash

# Placer.ai MCP Helm Chart Uninstallation Script
#
# Usage:
#   ./uninstall.sh [release-name] [options]
#
# Environment Variables:
#   NAMESPACE - Kubernetes namespace (optional, defaults to 'mcp-servers')
#
# Examples:
#   ./uninstall.sh                    # Uninstall with default release name
#   ./uninstall.sh my-placer-ai-mcp   # Uninstall with custom release name
#   ./uninstall.sh --dry-run          # Show what would be deleted
#   NAMESPACE=placer ./uninstall.sh   # Uninstall from 'placer' namespace

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

print_color $BLUE "🗑️  Placer.ai MCP Helm Chart Uninstaller"
echo ""

# Initialize variables
DRY_RUN=false
RELEASE_NAME=""
PURGE_NAMESPACE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --purge-namespace)
            PURGE_NAMESPACE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [release-name] [options]"
            echo ""
            echo "Options:"
            echo "  --dry-run           Show what would be deleted without actually deleting"
            echo "  --purge-namespace   Also delete the namespace (if empty)"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  NAMESPACE - Kubernetes namespace (defaults to 'mcp-servers')"
            echo ""
            echo "Examples:"
            echo "  $0                          # Basic uninstallation"
            echo "  $0 --dry-run                # Show what would be deleted"
            echo "  $0 --purge-namespace        # Also delete namespace if empty"
            exit 0
            ;;
        *)
            if [ -z "$RELEASE_NAME" ]; then
                RELEASE_NAME="$1"
            fi
            shift
            ;;
    esac
done

# Set defaults
if [ -z "$RELEASE_NAME" ]; then
    RELEASE_NAME="placer-ai-mcp"
fi

if [ -z "$NAMESPACE" ]; then
    NAMESPACE="mcp-servers"
fi

print_color $YELLOW "📋 Configuration:"
echo "   Release Name: $RELEASE_NAME"
echo "   Namespace: $NAMESPACE"
if [ "$DRY_RUN" = true ]; then
    echo "   Mode: Dry Run"
else
    echo "   Mode: Uninstall"
fi
if [ "$PURGE_NAMESPACE" = true ]; then
    echo "   Purge Namespace: Yes"
fi
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_color $RED "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    print_color $RED "❌ Helm not found. Please install Helm first."
    exit 1
fi

# Check if we can connect to the cluster
if ! kubectl cluster-info &> /dev/null; then
    print_color $RED "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

print_color $GREEN "✅ Kubernetes cluster connection verified"

# Check if release exists
if ! helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
    print_color $YELLOW "⚠️  Release '$RELEASE_NAME' not found in namespace '$NAMESPACE'"
    echo ""
    print_color $BLUE "📋 Available releases in namespace '$NAMESPACE':"
    helm list -n "$NAMESPACE"
    exit 1
fi

# Show what will be deleted
print_color $BLUE "🔍 Current release status:"
helm status "$RELEASE_NAME" -n "$NAMESPACE"
echo ""

if [ "$DRY_RUN" = true ]; then
    print_color $YELLOW "📋 Dry run - would delete the following:"
    echo "   • Helm release: $RELEASE_NAME"
    echo "   • Namespace: $NAMESPACE (contents)"
    kubectl get all -l app.kubernetes.io/instance="$RELEASE_NAME" -n "$NAMESPACE" 2>/dev/null || true
    
    if [ "$PURGE_NAMESPACE" = true ]; then
        echo "   • Namespace: $NAMESPACE (if empty after release deletion)"
    fi
    
    print_color $BLUE "🗑️  To actually uninstall, run without --dry-run"
    exit 0
fi

# Confirmation prompt
print_color $RED "⚠️  This will permanently delete the Placer.ai MCP server deployment!"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_color $YELLOW "❌ Uninstallation cancelled"
    exit 0
fi

# Uninstall the release
print_color $BLUE "🗑️  Uninstalling Helm release..."
helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"

print_color $GREEN "✅ Helm release '$RELEASE_NAME' uninstalled"

# Optionally purge namespace if requested and empty
if [ "$PURGE_NAMESPACE" = true ]; then
    echo ""
    print_color $BLUE "🔍 Checking if namespace is empty..."
    
    # Check if namespace has any remaining resources
    REMAINING_RESOURCES=$(kubectl get all -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    
    if [ "$REMAINING_RESOURCES" -eq 0 ]; then
        print_color $BLUE "🗑️  Deleting empty namespace '$NAMESPACE'..."
        kubectl delete namespace "$NAMESPACE"
        print_color $GREEN "✅ Namespace '$NAMESPACE' deleted"
    else
        print_color $YELLOW "⚠️  Namespace '$NAMESPACE' still contains resources, skipping deletion"
        kubectl get all -n "$NAMESPACE"
    fi
fi

echo ""
print_color $GREEN "✅ Placer.ai MCP server uninstallation completed!"
echo ""
print_color $BLUE "📋 Next steps:"
echo "   • Verify removal: helm list -A | grep placer-ai-mcp"
echo "   • Check namespace: kubectl get all -n $NAMESPACE"
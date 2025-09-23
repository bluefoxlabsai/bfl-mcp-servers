#!/bin/bash

# Atlassian MCP Helm Chart Uninstallation Script
#
# Usage:
#   ./uninstall.sh [release-name] [options]
#
# Environment Variables:
#   NAMESPACE - Kubernetes namespace (optional, will prompt if not set, defaults to 'mcp-servers')
#
# Examples:
#   ./uninstall.sh                    # Uninstall with default release name
#   ./uninstall.sh my-atlassian-mcp      # Uninstall with custom release name
#   ./uninstall.sh --dry-run          # Show what would be deleted
#   NAMESPACE=atlassian ./uninstall.sh   # Uninstall from 'nasdaq' namespace

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

print_color $BLUE "🗑️  Atlassian MCP Helm Chart Uninstaller"
echo ""

# Initialize variables
RELEASE_NAME=""
DRY_RUN=false
KEEP_NAMESPACE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --keep-namespace)
            KEEP_NAMESPACE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [release-name] [options]"
            echo ""
            echo "Options:"
            echo "  --dry-run           Show what would be deleted (no actual deletion)"
            echo "  --keep-namespace    Keep the namespace after uninstalling"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  NAMESPACE - Kubernetes namespace (defaults to 'mcp-servers')"
            echo ""
            echo "Examples:"
            echo "  $0                              # Basic uninstallation"
            echo "  $0 my-release --keep-namespace  # Uninstall but keep namespace"
            echo "  $0 --dry-run                    # Show what would be deleted"
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

# Set default release name if not provided
if [ -z "$RELEASE_NAME" ]; then
    RELEASE_NAME="atlassian-mcp"
fi

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    print_color $RED "❌ Helm is not installed. Please install Helm first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_color $RED "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if we can connect to Kubernetes
if ! kubectl cluster-info &> /dev/null; then
    print_color $RED "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

print_color $GREEN "✅ Prerequisites check passed"

# Get namespace from user
if [ -z "$NAMESPACE" ]; then
    echo ""
    print_color $YELLOW "🏷️  Please enter the Kubernetes namespace (default: mcp-servers):"
    read NAMESPACE
    if [ -z "$NAMESPACE" ]; then
        NAMESPACE="mcp-servers"
    fi
fi

print_color $BLUE "🏷️  Using namespace: $NAMESPACE"
print_color $BLUE "📦 Uninstalling release: $RELEASE_NAME"

# Check if release exists
if ! helm list -n "$NAMESPACE" | grep -q "^$RELEASE_NAME"; then
    print_color $RED "❌ Release '$RELEASE_NAME' not found in namespace '$NAMESPACE'"
    print_color $YELLOW "Available releases in namespace '$NAMESPACE':"
    helm list -n "$NAMESPACE"
    exit 1
fi

# Show what will be deleted
if [ "$DRY_RUN" = true ]; then
    print_color $YELLOW "🔍 Dry run - showing what would be deleted:"
    echo ""
    print_color $BLUE "📦 Helm release:"
    helm list -n "$NAMESPACE" | grep "^$RELEASE_NAME"
    echo ""
    print_color $BLUE "📋 Kubernetes resources:"
    helm get manifest "$RELEASE_NAME" -n "$NAMESPACE" | kubectl --dry-run=client -f - delete
    exit 0
fi

# Confirm deletion
echo ""
print_color $YELLOW "⚠️  This will permanently delete the following:"
print_color $YELLOW "   - Helm release: $RELEASE_NAME"
print_color $YELLOW "   - All Kubernetes resources (pods, services, secrets, etc.)"
if [ "$KEEP_NAMESPACE" = false ] && [ "$NAMESPACE" != "default" ]; then
    print_color $YELLOW "   - Namespace: $NAMESPACE (if empty after uninstall)"
fi
echo ""
print_color $YELLOW "Are you sure you want to continue? (y/N):"
read -r CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    print_color $BLUE "❌ Uninstallation cancelled."
    exit 0
fi

# Uninstall the release
print_color $YELLOW "�️  Uninstalling Atlassian MCP..."
helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"

if [ $? -eq 0 ]; then
    print_color $GREEN "✅ Helm release uninstalled successfully!"
    
    # Check if namespace is empty and should be deleted
    if [ "$KEEP_NAMESPACE" = false ] && [ "$NAMESPACE" != "default" ]; then
        REMAINING_RESOURCES=$(kubectl get all -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
        if [ "$REMAINING_RESOURCES" -eq 0 ]; then
            print_color $YELLOW "🗑️  Deleting empty namespace: $NAMESPACE"
            kubectl delete namespace "$NAMESPACE"
            print_color $GREEN "✅ Namespace deleted successfully!"
        else
            print_color $BLUE "ℹ️  Namespace '$NAMESPACE' contains other resources, keeping it."
        fi
    fi
    
    echo ""
    print_color $GREEN "🎉 Uninstallation completed successfully!"
    echo ""
    print_color $BLUE "💡 To reinstall, run:"
    echo "./install.sh $RELEASE_NAME"
    
else
    print_color $RED "❌ Uninstallation failed!"
    exit 1
fi
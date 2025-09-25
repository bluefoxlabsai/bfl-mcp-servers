#!/bin/bash

# Microsoft Teams MCP Helm Chart Uninstallation Script
#
# Usage:
#   ./uninstall.sh [release-name] [options]
#
# Examples:
#   ./uninstall.sh                    # Uninstall default release with prompts
#   ./uninstall.sh my-teams-mcp       # Uninstall specific release
#   ./uninstall.sh --dry-run          # See what would be deleted
#   ./uninstall.sh --keep-namespace   # Don't delete the namespace
#   NAMESPACE=teams ./uninstall.sh teams-mcp  # Non-interactive

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

print_color $BLUE "🗑️  Microsoft Teams MCP Helm Chart Uninstaller"
echo ""

# Initialize variables
DRY_RUN=false
RELEASE_NAME=""
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
            echo "  --dry-run           Show what would be deleted without actually deleting"
            echo "  --keep-namespace    Don't delete the namespace after uninstalling"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  NAMESPACE      - Kubernetes namespace (will prompt if not set)"
            echo ""
            echo "Examples:"
            echo "  $0                    # Basic uninstallation with prompts"
            echo "  $0 my-teams-mcp       # Uninstall specific release"
            echo "  $0 --dry-run          # Preview what would be deleted"
            echo "  $0 --keep-namespace   # Keep the namespace after uninstall"
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
    RELEASE_NAME="teams-mcp"
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

# Get namespace from user if not set
if [ -z "$NAMESPACE" ]; then
    echo ""
    print_color $YELLOW "🏷️  Please enter the Kubernetes namespace (default: mcp-servers):"
    read NAMESPACE
    if [ -z "$NAMESPACE" ]; then
        NAMESPACE="mcp-servers"
    fi
fi

print_color $BLUE "🏷️  Using namespace: $NAMESPACE"
print_color $BLUE "📦 Release name: $RELEASE_NAME"

# Check if release exists
if ! helm list -n "$NAMESPACE" | grep -q "^$RELEASE_NAME"; then
    print_color $RED "❌ Release '$RELEASE_NAME' not found in namespace '$NAMESPACE'"
    print_color $YELLOW "Available releases in namespace '$NAMESPACE':"
    helm list -n "$NAMESPACE"
    exit 1
fi

print_color $GREEN "✅ Found release '$RELEASE_NAME' in namespace '$NAMESPACE'"

if [ "$DRY_RUN" = true ]; then
    print_color $YELLOW "🔍 Dry run - showing what would be deleted:"
    echo ""
    print_color $BLUE "📋 Helm release resources:"
    helm get manifest "$RELEASE_NAME" -n "$NAMESPACE"
    echo ""
    print_color $BLUE "📋 Would run: helm uninstall $RELEASE_NAME -n $NAMESPACE"
    
    if [ "$KEEP_NAMESPACE" = false ]; then
        # Check if namespace would be empty after uninstall
        OTHER_RELEASES=$(helm list -n "$NAMESPACE" --short | grep -v "^$RELEASE_NAME$" | wc -l)
        if [ "$OTHER_RELEASES" -eq 0 ]; then
            print_color $BLUE "📋 Would also delete namespace '$NAMESPACE' (no other releases found)"
        else
            print_color $BLUE "📋 Would keep namespace '$NAMESPACE' (contains other releases)"
        fi
    else
        print_color $BLUE "📋 Would keep namespace '$NAMESPACE' (--keep-namespace flag)"
    fi
    
    print_color $GREEN "✅ Dry run completed"
    exit 0
fi

# Confirm deletion
echo ""
print_color $YELLOW "⚠️  This will permanently delete the Microsoft Teams MCP server deployment."
print_color $YELLOW "   Release: $RELEASE_NAME"
print_color $YELLOW "   Namespace: $NAMESPACE"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_color $BLUE "❌ Uninstallation cancelled"
    exit 0
fi

# Uninstall the Helm release
print_color $YELLOW "🔧 Uninstalling Microsoft Teams MCP..."
helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"

if [ $? -eq 0 ]; then
    print_color $GREEN "✅ Successfully uninstalled release '$RELEASE_NAME'"
    
    # Check if we should delete the namespace
    if [ "$KEEP_NAMESPACE" = false ] && [ "$NAMESPACE" != "default" ]; then
        # Check if namespace is empty (no other helm releases)
        OTHER_RELEASES=$(helm list -n "$NAMESPACE" --short 2>/dev/null | wc -l)
        
        if [ "$OTHER_RELEASES" -eq 0 ]; then
            print_color $YELLOW "🔧 Namespace '$NAMESPACE' is empty, deleting it..."
            kubectl delete namespace "$NAMESPACE" 2>/dev/null || true
            
            if [ $? -eq 0 ]; then
                print_color $GREEN "✅ Successfully deleted namespace '$NAMESPACE'"
            else
                print_color $YELLOW "⚠️  Namespace '$NAMESPACE' may have already been deleted or contains other resources"
            fi
        else
            print_color $BLUE "ℹ️  Keeping namespace '$NAMESPACE' (contains other Helm releases)"
        fi
    else
        if [ "$KEEP_NAMESPACE" = true ]; then
            print_color $BLUE "ℹ️  Keeping namespace '$NAMESPACE' (--keep-namespace flag)"
        else
            print_color $BLUE "ℹ️  Keeping default namespace"
        fi
    fi
    
    echo ""
    print_color $GREEN "🎉 Microsoft Teams MCP has been successfully uninstalled!"
    echo ""
    print_color $BLUE "📋 To verify removal:"
    echo "kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=teams-mcp"
    echo "helm list -n $NAMESPACE"
    
else
    print_color $RED "❌ Failed to uninstall release '$RELEASE_NAME'"
    exit 1
fi
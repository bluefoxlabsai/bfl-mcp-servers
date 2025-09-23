#!/bin/bash

# Google Search MCP Helm Chart Uninstallation Script
#
# Usage:
#   ./uninstall.sh [release-name] [options]
#
# Environment Variables:
#   NAMESPACE - Kubernetes namespace (optional, will prompt if not set, defaults to 'mcp-servers')
#
# Examples:
#   ./uninstall.sh                         # Uninstall with default release name
#   ./uninstall.sh my-google-search-mcp    # Uninstall with custom release name
#   ./uninstall.sh --dry-run               # Show what would be deleted
#   NAMESPACE=google ./uninstall.sh        # Uninstall from 'google' namespace

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

print_color $BLUE "🗑️  Google Search MCP Helm Chart Uninstaller"
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
    RELEASE_NAME="google-search-mcp"
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
print_color $BLUE "📦 Release name: $RELEASE_NAME"

# Check if release exists
if ! helm list -n "$NAMESPACE" | grep -q "^$RELEASE_NAME"; then
    print_color $RED "❌ Release '$RELEASE_NAME' not found in namespace '$NAMESPACE'"
    print_color $YELLOW "Available releases:"
    helm list -n "$NAMESPACE"
    exit 1
fi

# Show what will be deleted
print_color $YELLOW "🔍 Checking what will be deleted:"
echo ""

if [ "$DRY_RUN" = true ]; then
    print_color $BLUE "📋 Resources that would be deleted:"
    helm template "$RELEASE_NAME" --namespace "$NAMESPACE" | kubectl delete --dry-run=client -f - 2>/dev/null || true
    echo ""
    print_color $YELLOW "Note: This is a dry run. No actual deletion will occur."
    exit 0
fi

# Get current release info
RELEASE_INFO=$(helm get all "$RELEASE_NAME" -n "$NAMESPACE" 2>/dev/null)
if [ $? -eq 0 ]; then
    print_color $BLUE "📊 Current release information:"
    echo "Release: $RELEASE_NAME"
    echo "Namespace: $NAMESPACE"
    helm list -n "$NAMESPACE" | grep "^$RELEASE_NAME" || true
    echo ""
fi

# Confirm deletion
echo ""
print_color $YELLOW "⚠️  This will permanently delete the Google Search MCP deployment."
print_color $YELLOW "   All data and configurations will be lost."
echo ""
print_color $YELLOW "Do you want to continue? (y/N):"
read -r CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    print_color $BLUE "❌ Uninstallation cancelled."
    exit 0
fi

# Perform uninstallation
print_color $YELLOW "🗑️  Uninstalling Google Search MCP..."
helm uninstall "$RELEASE_NAME" --namespace "$NAMESPACE"

if [ $? -eq 0 ]; then
    print_color $GREEN "✅ Release '$RELEASE_NAME' successfully uninstalled from namespace '$NAMESPACE'"
    
    # Check if namespace should be deleted
    if [ "$KEEP_NAMESPACE" = false ] && [ "$NAMESPACE" != "default" ]; then
        echo ""
        print_color $YELLOW "🏷️  Do you want to delete the namespace '$NAMESPACE'? (y/N):"
        read -r DELETE_NAMESPACE
        
        if [[ "$DELETE_NAMESPACE" =~ ^[Yy]$ ]]; then
            # Check if namespace has other resources
            OTHER_RESOURCES=$(kubectl get all -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
            if [ "$OTHER_RESOURCES" -gt 0 ]; then
                print_color $YELLOW "⚠️  Namespace '$NAMESPACE' contains other resources:"
                kubectl get all -n "$NAMESPACE" 2>/dev/null || true
                echo ""
                print_color $YELLOW "Do you still want to delete the namespace? This will delete ALL resources in it. (y/N):"
                read -r FORCE_DELETE_NAMESPACE
                
                if [[ "$FORCE_DELETE_NAMESPACE" =~ ^[Yy]$ ]]; then
                    kubectl delete namespace "$NAMESPACE"
                    print_color $GREEN "✅ Namespace '$NAMESPACE' deleted"
                else
                    print_color $BLUE "🏷️  Namespace '$NAMESPACE' preserved"
                fi
            else
                kubectl delete namespace "$NAMESPACE"
                print_color $GREEN "✅ Empty namespace '$NAMESPACE' deleted"
            fi
        else
            print_color $BLUE "🏷️  Namespace '$NAMESPACE' preserved"
        fi
    else
        print_color $BLUE "🏷️  Namespace '$NAMESPACE' preserved"
    fi
    
    echo ""
    print_color $GREEN "🎉 Google Search MCP uninstallation completed!"
    echo ""
    print_color $BLUE "📋 To reinstall, you can run:"
    echo "./install.sh $RELEASE_NAME"
    
else
    print_color $RED "❌ Uninstallation failed!"
    echo ""
    print_color $YELLOW "🔍 Troubleshooting tips:"
    echo "1. Check if the release exists: helm list -n $NAMESPACE"
    echo "2. Check for finalizers: kubectl get all -n $NAMESPACE"
    echo "3. Force delete if necessary: helm uninstall $RELEASE_NAME -n $NAMESPACE --no-hooks"
    exit 1
fi
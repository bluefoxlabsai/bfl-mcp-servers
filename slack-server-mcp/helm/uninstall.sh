#!/bin/bash

# Slack MCP Server Helm Chart Uninstallation Script
#
# Usage:
#   ./uninstall.sh [release-name] [options]
#
# Environment Variables:
#   NAMESPACE - Kubernetes namespace (optional, will prompt if not set, defaults to 'mcp-servers')
#
# Examples:
#   ./uninstall.sh                      # Uninstall with default release name
#   ./uninstall.sh my-slack-server      # Uninstall with custom release name
#   ./uninstall.sh --dry-run            # Show what would be deleted
#   NAMESPACE=slack ./uninstall.sh      # Uninstall from 'slack' namespace

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

print_color $BLUE "🗑️  Slack MCP Server Helm Chart Uninstaller"
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
            cat << EOF
Slack MCP Server Helm Chart Uninstallation Script

Usage:
    $0 [release-name] [options]

Arguments:
    release-name    Name of the Helm release to uninstall (optional, defaults to 'slack-mcp-server')

Options:
    --dry-run           Show what would be deleted without actually deleting
    --keep-namespace    Keep the namespace after uninstalling (don't delete it)
    -h, --help          Show this help message

Environment Variables:
    NAMESPACE          Kubernetes namespace (default: mcp-servers)

Examples:
    $0                           # Basic uninstallation with prompts
    $0 my-slack-server           # Uninstall specific release
    $0 --dry-run                 # Show what would be deleted
    $0 --keep-namespace          # Keep namespace after uninstall
    NAMESPACE=slack $0           # Uninstall from custom namespace

For more information, visit:
https://github.com/bluefoxlabsai/bfl-mcp-servers/tree/main/slack-server-mcp/helm
EOF
            exit 0
            ;;
        -*)
            print_color $RED "❌ Unknown option: $1"
            print_color $YELLOW "Use --help for usage information"
            exit 1
            ;;
        *)
            if [[ -z "$RELEASE_NAME" ]]; then
                RELEASE_NAME="$1"
            else
                print_color $RED "❌ Unexpected argument: $1"
                exit 1
            fi
            shift
            ;;
    esac
done

# Set default release name if not provided
if [[ -z "$RELEASE_NAME" ]]; then
    RELEASE_NAME="slack-server-mcp"
fi

print_color $PURPLE "📋 Configuration Summary:"
echo "  Release Name: $RELEASE_NAME"
echo "  Dry Run: $DRY_RUN"
echo "  Keep Namespace: $KEEP_NAMESPACE"
echo ""

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    print_color $RED "❌ Helm is not installed or not in PATH"
    print_color $YELLOW "Please install Helm from: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_color $RED "❌ kubectl is not installed or not in PATH"
    print_color $YELLOW "Please install kubectl and configure it to connect to your cluster"
    exit 1
fi

# Check if we can connect to Kubernetes cluster
if ! kubectl cluster-info &> /dev/null; then
    print_color $RED "❌ Cannot connect to Kubernetes cluster"
    print_color $YELLOW "Please ensure kubectl is configured correctly"
    exit 1
fi

# Get namespace
if [[ -z "$NAMESPACE" ]]; then
    echo ""
    print_color $BLUE "🏷️  Kubernetes Namespace Configuration"
    read -p "Enter the namespace to uninstall from (default: mcp-servers): " NAMESPACE
    NAMESPACE=${NAMESPACE:-mcp-servers}
fi

print_color $GREEN "✅ Using namespace: $NAMESPACE"

# Check if the namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_color $RED "❌ Namespace '$NAMESPACE' does not exist"
    exit 1
fi

# Check if the release exists
if ! helm list -n "$NAMESPACE" | grep -q "^$RELEASE_NAME\s"; then
    print_color $RED "❌ Helm release '$RELEASE_NAME' not found in namespace '$NAMESPACE'"
    print_color $YELLOW "Available releases in namespace '$NAMESPACE':"
    helm list -n "$NAMESPACE" --output table
    exit 1
fi

# Show what will be uninstalled
echo ""
print_color $PURPLE "🎯 Uninstallation Summary:"
echo "  Release Name: $RELEASE_NAME"
echo "  Namespace: $NAMESPACE"

# Get release information
print_color $BLUE "📊 Current release information:"
helm list -n "$NAMESPACE" | grep "^$RELEASE_NAME\s" || true
echo ""

# Show resources that will be deleted
print_color $BLUE "📦 Resources that will be deleted:"
if [[ "$DRY_RUN" == "true" ]]; then
    print_color $YELLOW "(dry-run mode - showing current resources)"
fi

# List Kubernetes resources
kubectl get all -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME" 2>/dev/null || print_color $YELLOW "  No resources found with label app.kubernetes.io/instance=$RELEASE_NAME"

# List secrets
SECRETS=$(kubectl get secrets -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME" --no-headers 2>/dev/null | awk '{print $1}' || true)
if [[ -n "$SECRETS" ]]; then
    echo ""
    print_color $YELLOW "🔐 Secrets that will be deleted:"
    echo "$SECRETS" | while read secret; do
        echo "  - $secret"
    done
fi

# List configmaps
CONFIGMAPS=$(kubectl get configmaps -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME" --no-headers 2>/dev/null | awk '{print $1}' || true)
if [[ -n "$CONFIGMAPS" ]]; then
    echo ""
    print_color $YELLOW "📄 ConfigMaps that will be deleted:"
    echo "$CONFIGMAPS" | while read cm; do
        echo "  - $cm"
    done
fi

echo ""

# Ask for confirmation unless it's a dry run
if [[ "$DRY_RUN" == "false" ]]; then
    print_color $RED "⚠️  WARNING: This will permanently delete the Slack MCP Server and all its data!"
    echo ""
    read -p "Are you sure you want to uninstall '$RELEASE_NAME'? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_color $YELLOW "🚫 Uninstallation cancelled"
        exit 0
    fi
fi

# Perform uninstallation
echo ""
if [[ "$DRY_RUN" == "true" ]]; then
    print_color $BLUE "🔍 Running dry-run validation..."
    print_color $YELLOW "This would uninstall release '$RELEASE_NAME' from namespace '$NAMESPACE'"
else
    print_color $BLUE "🗑️  Uninstalling Slack MCP Server..."
    
    # Uninstall Helm release
    if helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"; then
        print_color $GREEN "✅ Helm release '$RELEASE_NAME' uninstalled successfully"
    else
        print_color $RED "❌ Failed to uninstall Helm release"
        exit 1
    fi
    
    # Wait a moment for resources to be deleted
    sleep 2
    
    # Check for remaining resources
    print_color $BLUE "🔍 Checking for remaining resources..."
    REMAINING_RESOURCES=$(kubectl get all -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME" --no-headers 2>/dev/null || true)
    
    if [[ -n "$REMAINING_RESOURCES" ]]; then
        print_color $YELLOW "⚠️  Some resources are still being deleted..."
        echo "$REMAINING_RESOURCES"
        print_color $BLUE "Waiting for resources to be fully deleted..."
        
        # Wait up to 60 seconds for resources to be deleted
        for i in {1..12}; do
            sleep 5
            REMAINING_RESOURCES=$(kubectl get all -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME" --no-headers 2>/dev/null || true)
            if [[ -z "$REMAINING_RESOURCES" ]]; then
                break
            fi
            print_color $BLUE "Still waiting... ($((i*5))s)"
        done
        
        # Final check
        REMAINING_RESOURCES=$(kubectl get all -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME" --no-headers 2>/dev/null || true)
        if [[ -n "$REMAINING_RESOURCES" ]]; then
            print_color $YELLOW "⚠️  Some resources may still be terminating:"
            echo "$REMAINING_RESOURCES"
        fi
    fi
    
    print_color $GREEN "✅ All application resources have been deleted"
fi

# Handle namespace deletion
if [[ "$KEEP_NAMESPACE" == "false" && "$DRY_RUN" == "false" ]]; then
    echo ""
    print_color $BLUE "🏷️  Namespace Management"
    
    # Check if there are other resources in the namespace
    OTHER_RESOURCES=$(kubectl get all -n "$NAMESPACE" --no-headers 2>/dev/null | grep -v "^service/kubernetes" || true)
    
    if [[ -z "$OTHER_RESOURCES" ]]; then
        read -p "The namespace '$NAMESPACE' appears to be empty. Delete it? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if kubectl delete namespace "$NAMESPACE"; then
                print_color $GREEN "✅ Namespace '$NAMESPACE' deleted successfully"
            else
                print_color $YELLOW "⚠️  Failed to delete namespace '$NAMESPACE'"
            fi
        else
            print_color $BLUE "ℹ️  Keeping namespace '$NAMESPACE'"
        fi
    else
        print_color $BLUE "ℹ️  Namespace '$NAMESPACE' contains other resources - keeping it"
    fi
fi

# Final summary
echo ""
if [[ "$DRY_RUN" == "true" ]]; then
    print_color $GREEN "✅ Dry-run completed successfully!"
    print_color $YELLOW "Remove --dry-run flag to perform actual uninstallation"
else
    print_color $GREEN "🎉 Slack MCP Server uninstalled successfully!"
    echo ""
    print_color $BLUE "📋 Cleanup completed:"
    echo "  ✅ Helm release '$RELEASE_NAME' removed"
    echo "  ✅ Kubernetes resources deleted"
    echo "  ✅ Secrets and ConfigMaps removed"
    if [[ "$KEEP_NAMESPACE" == "false" ]]; then
        echo "  ✅ Namespace handling completed"
    else
        echo "  ℹ️  Namespace '$NAMESPACE' preserved (--keep-namespace flag)"
    fi
    echo ""
    print_color $YELLOW "💡 Note: Any persistent volumes or external resources may need to be cleaned up manually"
fi
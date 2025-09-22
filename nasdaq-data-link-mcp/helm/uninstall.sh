#!/bin/bash

# Nasdaq Data Link MCP Helm Chart Uninstallation Script
#
# Usage:
#   ./uninstall.sh [release-name] [namespace]
#
# Examples:
#   ./uninstall.sh                           # Uninstall default release from default namespace
#   ./uninstall.sh my-nasdaq-mcp             # Uninstall custom release from default namespace
#   ./uninstall.sh nasdaq-mcp nasdaq         # Uninstall from specific namespace

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

print_color $BLUE "🗑️  Nasdaq Data Link MCP Helm Chart Uninstaller"
echo ""

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

# Get release name and namespace
RELEASE_NAME=${1:-nasdaq-mcp}
NAMESPACE=${2:-default}

print_color $BLUE "📦 Uninstalling release: $RELEASE_NAME from namespace: $NAMESPACE"

# Check if release exists
if ! helm status "$RELEASE_NAME" --namespace "$NAMESPACE" &> /dev/null; then
    print_color $YELLOW "⚠️  Release $RELEASE_NAME not found in namespace $NAMESPACE"
    print_color $BLUE "📋 Available releases:"
    helm list --namespace "$NAMESPACE"
    exit 1
fi

# Show what will be uninstalled
print_color $YELLOW "🔍 Release information:"
helm status "$RELEASE_NAME" --namespace "$NAMESPACE"
echo ""

# Confirm uninstallation
print_color $YELLOW "⚠️  Are you sure you want to uninstall $RELEASE_NAME from namespace $NAMESPACE? (y/N)"
read -r CONFIRM

if [[ $CONFIRM =~ ^[Yy]$ ]]; then
    print_color $YELLOW "🔧 Uninstalling Nasdaq Data Link MCP..."
    
    helm uninstall "$RELEASE_NAME" --namespace "$NAMESPACE"
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Uninstallation completed successfully!"
        echo ""
        
        # Check if namespace is empty and can be deleted (except default)
        if [ "$NAMESPACE" != "default" ] && [ "$NAMESPACE" != "kube-system" ]; then
            REMAINING_RESOURCES=$(kubectl get all --namespace "$NAMESPACE" 2>/dev/null | grep -v "^NAME" | wc -l)
            if [ "$REMAINING_RESOURCES" -eq 0 ]; then
                print_color $YELLOW "🤔 Namespace $NAMESPACE appears to be empty. Delete it? (y/N)"
                read -r DELETE_NS
                if [[ $DELETE_NS =~ ^[Yy]$ ]]; then
                    kubectl delete namespace "$NAMESPACE"
                    print_color $GREEN "✅ Namespace $NAMESPACE deleted"
                fi
            fi
        fi
        
        print_color $BLUE "📊 To verify cleanup, run:"
        echo "kubectl get pods --namespace $NAMESPACE -l app.kubernetes.io/name=nasdaq-data-link-mcp"
    else
        print_color $RED "❌ Uninstallation failed!"
        exit 1
    fi
else
    print_color $BLUE "❌ Uninstallation cancelled"
    exit 0
fi
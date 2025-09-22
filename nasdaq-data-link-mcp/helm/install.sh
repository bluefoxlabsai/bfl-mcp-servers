#!/bin/bash

# Nasdaq Data Link MCP Helm Chart Installation Script
#
# Usage:
#   ./install.sh [release-name]
#
# Environment Variables:
#   NASDAQ_API_KEY - Your Nasdaq Data Link API key (optional, will prompt if not set)
#   NAMESPACE      - Kubernetes namespace (optional, will prompt if not set, defaults to 'default')
#
# Examples:
#   ./install.sh                    # Install with default release name and prompts
#   ./install.sh my-nasdaq-mcp      # Install with custom release name
#   NASDAQ_API_KEY=xyz ./install.sh # Install with pre-set API key
#   NAMESPACE=nasdaq ./install.sh   # Install in 'nasdaq' namespace

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

print_color $BLUE "🚀 Nasdaq Data Link MCP Helm Chart Installer"
echo ""

# Parse command line arguments
DRY_RUN=false
RELEASE_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [release-name] [--dry-run] [--help]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Perform a dry run (template only, no actual installation)"
            echo "  -h, --help   Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  NASDAQ_API_KEY - Your Nasdaq Data Link API key"
            echo "  NAMESPACE      - Kubernetes namespace (defaults to 'default')"
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
    RELEASE_NAME="nasdaq-mcp"
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
    print_color $YELLOW "🏷️  Please enter the Kubernetes namespace (default: default):"
    read NAMESPACE
    if [ -z "$NAMESPACE" ]; then
        NAMESPACE="default"
    fi
fi

print_color $BLUE "🏷️  Using namespace: $NAMESPACE"

# Create namespace if it doesn't exist
if [ "$NAMESPACE" != "default" ] && [ "$DRY_RUN" = false ]; then
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        print_color $YELLOW "🔧 Creating namespace: $NAMESPACE"
        kubectl create namespace "$NAMESPACE"
    else
        print_color $GREEN "✅ Namespace $NAMESPACE already exists"
    fi
elif [ "$NAMESPACE" != "default" ] && [ "$DRY_RUN" = true ]; then
    print_color $YELLOW "🔧 Would create namespace: $NAMESPACE (dry-run mode)"
fi

print_color $BLUE "📦 Installing with release name: $RELEASE_NAME"

# Determine the chart path based on where the script is run from
if [ -f "Chart.yaml" ]; then
    CHART_PATH="."
elif [ -f "helm-chart/Chart.yaml" ]; then
    CHART_PATH="./helm-chart"
else
    print_color $RED "❌ Cannot find Chart.yaml. Please run this script from the project root or helm-chart directory."
    exit 1
fi

# Install the chart

# Get API key from user
if [ -z "$NASDAQ_API_KEY" ]; then
    echo ""
    print_color $YELLOW "📋 Please enter your Nasdaq Data Link API key:"
    read -s NASDAQ_API_KEY
    echo ""
fi

if [ -z "$NASDAQ_API_KEY" ]; then
    print_color $RED "❌ API key is required. Please set NASDAQ_API_KEY environment variable or enter it when prompted."
    exit 1
fi

# Parse command line arguments
DRY_RUN=false
RELEASE_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [release-name] [--dry-run] [--help]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Perform a dry run (template only, no actual installation)"
            echo "  -h, --help   Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  NASDAQ_API_KEY - Your Nasdaq Data Link API key"
            echo "  NAMESPACE      - Kubernetes namespace (defaults to 'default')"
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
    RELEASE_NAME="nasdaq-mcp"
fi

# Install the chart
if [ "$DRY_RUN" = true ]; then
    print_color $YELLOW "🔧 Dry run - templating Nasdaq Data Link MCP..."
    helm template "$RELEASE_NAME" "$CHART_PATH" \
        --namespace "$NAMESPACE" \
        --set secret.nasdaqApiKey="$NASDAQ_API_KEY"
else
    print_color $YELLOW "🔧 Installing Nasdaq Data Link MCP..."
    helm install "$RELEASE_NAME" "$CHART_PATH" \
        --namespace "$NAMESPACE" \
        --set secret.nasdaqApiKey="$NASDAQ_API_KEY" \
        --timeout=5m
fi

if [ $? -eq 0 ] && [ "$DRY_RUN" = false ]; then
    print_color $GREEN "✅ Installation completed successfully!"
    echo ""
    print_color $BLUE "🔗 To access the MCP server:"
    
    # Check which transport is being used by looking at values or using helm get
    TRANSPORT=$(helm get values "$RELEASE_NAME" --namespace "$NAMESPACE" -o json 2>/dev/null | grep -o '"transport":"[^"]*"' | cut -d'"' -f4 || echo "streamable-http")
    
    if [ "$TRANSPORT" = "stdio" ]; then
        print_color $BLUE "📋 For stdio transport (kubectl exec):"
        echo "export POD_NAME=\$(kubectl get pods --namespace $NAMESPACE -l \"app.kubernetes.io/name=nasdaq-data-link-mcp,app.kubernetes.io/instance=$RELEASE_NAME\" -o jsonpath=\"{.items[0].metadata.name}\")"
        echo "kubectl exec -it \$POD_NAME --namespace $NAMESPACE -- python nasdaq_data_link_mcp_os/server.py"
    else
        print_color $BLUE "📋 For HTTP transport:"
        echo "kubectl --namespace $NAMESPACE port-forward service/$RELEASE_NAME-nasdaq-data-link-mcp 8080:8080"
        echo "Then access: http://localhost:8080/health"
        echo ""
        print_color $BLUE "📖 For LibreChat integration:"
        echo "mcpServers:"
        echo "  nasdaq-data-link-mcp:"
        echo "    type: \"streamable-http\""
        echo "    url: \"http://localhost:8080\""
        echo "    timeout: 30000"
    fi
    
    echo ""
    print_color $YELLOW "📊 To check the deployment status, run:"
    echo "kubectl get pods --namespace $NAMESPACE -l app.kubernetes.io/name=nasdaq-data-link-mcp"
    echo "kubectl logs --namespace $NAMESPACE -l app.kubernetes.io/name=nasdaq-data-link-mcp"
elif [ "$DRY_RUN" = true ]; then
    print_color $GREEN "✅ Dry run completed successfully!"
else
    print_color $RED "❌ Installation failed!"
    exit 1
fi
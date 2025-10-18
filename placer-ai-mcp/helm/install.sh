#!/bin/bash

# Placer.ai MCP Helm Chart Installation Script
#
# Usage:
#   ./install.sh [release-name] [options]
#
# Environment Variables:
#   PLACER_AI_API_KEY - Your Placer.ai API key (optional, will prompt if not set)
#   NAMESPACE         - Kubernetes namespace (optional, defaults to 'mcp-servers')
#
# Examples:
#   ./install.sh                              # Install with default release name and prompts
#   ./install.sh my-placer-ai-mcp             # Install with custom release name
#   PLACER_AI_API_KEY=xyz ./install.sh        # Install with pre-set API key
#   NAMESPACE=placer ./install.sh             # Install in 'placer' namespace
#   ./install.sh --upgrade                    # Upgrade existing installation
#   ./install.sh --image-tag=v0.1.0           # Install with specific image tag

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

print_color $BLUE "🚀 Placer.ai MCP Helm Chart Installer"
echo ""

# Initialize variables
DRY_RUN=false
RELEASE_NAME=""
UPGRADE=false
IMAGE_TAG="latest"
VALUES_FILE=""
FORCE_PULL=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --upgrade)
            UPGRADE=true
            shift
            ;;
        --image-tag=*)
            IMAGE_TAG="${1#*=}"
            shift
            ;;
        --image-tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -f|--values)
            VALUES_FILE="$2"
            shift 2
            ;;
        --force-pull)
            FORCE_PULL=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [release-name] [options]"
            echo ""
            echo "Options:"
            echo "  --dry-run           Perform a dry run (template only, no actual installation)"
            echo "  --upgrade           Upgrade existing installation instead of install"
            echo "  --image-tag=TAG     Specify Docker image tag (default: latest)"
            echo "  --force-pull        Force pull latest image (sets pullPolicy=Always)"
            echo "  -f, --values FILE   Specify custom values file"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  PLACER_AI_API_KEY - Your Placer.ai API key"
            echo "  NAMESPACE         - Kubernetes namespace (defaults to 'mcp-servers')"
            echo ""
            echo "Examples:"
            echo "  $0                              # Basic installation"
            echo "  $0 --upgrade --image-tag=v0.1.0 # Upgrade to specific version"
            echo "  $0 --force-pull                 # Force pull latest image"
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
echo "   Image Tag: $IMAGE_TAG"
if [ "$DRY_RUN" = true ]; then
    echo "   Mode: Dry Run"
elif [ "$UPGRADE" = true ]; then
    echo "   Mode: Upgrade"
else
    echo "   Mode: Install"
fi
if [ -n "$VALUES_FILE" ]; then
    echo "   Values File: $VALUES_FILE"
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

# Prompt for API key if not set
if [ -z "$PLACER_AI_API_KEY" ]; then
    print_color $YELLOW "🔑 Placer.ai API Key Required"
    echo "   Get your API key from: https://www.placer.ai/"
    echo ""
    read -s -p "Enter your Placer.ai API key: " PLACER_AI_API_KEY
    echo ""
    if [ -z "$PLACER_AI_API_KEY" ]; then
        print_color $RED "❌ API key is required"
        exit 1
    fi
fi

# Create namespace if it doesn't exist
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_color $YELLOW "📁 Creating namespace: $NAMESPACE"
    if [ "$DRY_RUN" = false ]; then
        kubectl create namespace "$NAMESPACE"
    else
        echo "kubectl create namespace $NAMESPACE"
    fi
fi

# Build helm command
HELM_CMD="helm"
if [ "$UPGRADE" = true ]; then
    HELM_CMD="$HELM_CMD upgrade"
else
    HELM_CMD="$HELM_CMD install"
fi

HELM_CMD="$HELM_CMD $RELEASE_NAME . --namespace $NAMESPACE"

# Add values
HELM_CMD="$HELM_CMD --set placerAI.apiKey=$PLACER_AI_API_KEY"
HELM_CMD="$HELM_CMD --set image.tag=$IMAGE_TAG"

if [ "$FORCE_PULL" = true ]; then
    HELM_CMD="$HELM_CMD --set image.pullPolicy=Always"
fi

if [ -n "$VALUES_FILE" ]; then
    HELM_CMD="$HELM_CMD -f $VALUES_FILE"
fi

if [ "$DRY_RUN" = true ]; then
    HELM_CMD="$HELM_CMD --dry-run --debug"
fi

if [ "$UPGRADE" = false ]; then
    HELM_CMD="$HELM_CMD --create-namespace"
fi

# Execute helm command
print_color $BLUE "🚀 Running Helm command..."
echo "   $HELM_CMD"
echo ""

eval $HELM_CMD

if [ "$DRY_RUN" = false ]; then
    echo ""
    print_color $GREEN "✅ Placer.ai MCP server deployment completed!"
    echo ""
    print_color $YELLOW "📋 Next steps:"
    echo "   • Check deployment status: kubectl get pods -n $NAMESPACE"
    echo "   • View logs: kubectl logs -f deployment/$RELEASE_NAME -n $NAMESPACE"
    echo "   • Port forward: kubectl port-forward service/$RELEASE_NAME 8000:8000 -n $NAMESPACE"
    echo "   • Test health: curl http://localhost:8000/health"
    echo ""
    print_color $BLUE "🔗 MCP Connection:"
    echo "   • Transport: streamable-http"
    echo "   • URL: http://$RELEASE_NAME.$NAMESPACE.svc.cluster.local:8000"
    echo "   • Local (port-forward): http://localhost:8000"
else
    print_color $YELLOW "📋 Dry run completed. Review the output above."
fi
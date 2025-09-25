#!/bin/bash

# SharePoint MCP Helm Chart Installation Script
#
# Usage:
#   ./install.sh [release-name] [options]
#
# Environment Variables:
#   SHAREPOINT_SITE_URL, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID - Your SharePoint credentials (optional, will prompt if not set)
#   NAMESPACE      - Kubernetes namespace (optional, will prompt if not set, defaults to 'mcp-servers')
#
# Examples:
#   ./install.sh                              # Install with default release name and prompts
#   ./install.sh my-sharepoint-mcp            # Install with custom release name
#   AZURE_CLIENT_ID=xyz ./install.sh          # Install with pre-set client ID
#   NAMESPACE=sharepoint ./install.sh         # Install in 'sharepoint' namespace
#   ./install.sh --upgrade                    # Upgrade existing installation
#   ./install.sh --image-tag=v0.2.4          # Install with specific image tag
#   ./install.sh -f values-prod.yaml          # Install with custom values file

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

print_color $BLUE "🚀 SharePoint MCP Helm Chart Installer"
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
            echo "  SHAREPOINT_SITE_URL, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID - Your SharePoint credentials"
            echo "  NAMESPACE      - Kubernetes namespace (defaults to 'mcp-servers')"
            echo ""
            echo "Examples:"
            echo "  $0                              # Basic installation"
            echo "  $0 --upgrade --image-tag=v0.2.4 # Upgrade to specific version"
            echo "  $0 -f examples/values-prod.yaml # Install with production config"
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

# Set default release name if not provided
if [ -z "$RELEASE_NAME" ]; then
    RELEASE_NAME="sharepoint-mcp"
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

# Check if release already exists (for upgrade detection)
if helm list -n "$NAMESPACE" | grep -q "^$RELEASE_NAME"; then
    if [ "$UPGRADE" = false ]; then
        print_color $YELLOW "⚠️  Release '$RELEASE_NAME' already exists in namespace '$NAMESPACE'"
        print_color $YELLOW "   Use --upgrade flag to upgrade, or choose a different release name"
        exit 1
    else
        print_color $BLUE "🔄 Upgrading existing release: $RELEASE_NAME"
    fi
else
    if [ "$UPGRADE" = true ]; then
        print_color $RED "❌ Cannot upgrade: Release '$RELEASE_NAME' not found in namespace '$NAMESPACE'"
        exit 1
    fi
fi

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
print_color $PURPLE "🏷️  Using image tag: $IMAGE_TAG"

# Determine the chart path based on where the script is run from
if [ -f "Chart.yaml" ]; then
    CHART_PATH="."
elif [ -f "helm-chart/Chart.yaml" ]; then
    CHART_PATH="./helm-chart"
else
    print_color $RED "❌ Cannot find Chart.yaml. Please run this script from the project root or helm-chart directory."
    exit 1
fi

# Get SharePoint credentials from user if not provided via environment
if [ -z "$SHAREPOINT_SITE_URL" ]; then
    echo ""
    print_color $YELLOW "📋 Please enter your SharePoint site URL (e.g., https://yourtenant.sharepoint.com/sites/yoursite):"
    read SHAREPOINT_SITE_URL
fi

if [ -z "$AZURE_CLIENT_ID" ]; then
    echo ""
    print_color $YELLOW "📋 Please enter your Azure AD client ID:"
    read AZURE_CLIENT_ID
fi

if [ -z "$AZURE_CLIENT_SECRET" ]; then
    echo ""
    print_color $YELLOW "📋 Please enter your Azure AD client secret:"
    read -s AZURE_CLIENT_SECRET
    echo ""
fi

if [ -z "$AZURE_TENANT_ID" ]; then
    echo ""
    print_color $YELLOW "📋 Please enter your Azure AD tenant ID:"
    read AZURE_TENANT_ID
fi

# Validate required credentials
if [ -z "$SHAREPOINT_SITE_URL" ] || [ -z "$AZURE_CLIENT_ID" ] || [ -z "$AZURE_CLIENT_SECRET" ] || [ -z "$AZURE_TENANT_ID" ]; then
    print_color $RED "❌ All SharePoint credentials are required. Please set environment variables or enter them when prompted."
    print_color $RED "   Required: SHAREPOINT_SITE_URL, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID"
    exit 1
fi

# Build Helm command arguments
HELM_ARGS=(
    --namespace "$NAMESPACE"
    --set secret.sharepointSiteUrl="$SHAREPOINT_SITE_URL"
    --set secret.azureClientId="$AZURE_CLIENT_ID"
    --set secret.azureClientSecret="$AZURE_CLIENT_SECRET"
    --set secret.azureTenantId="$AZURE_TENANT_ID"
    --set image.tag="$IMAGE_TAG"
    --timeout=5m
)

# Add force pull if requested
if [ "$FORCE_PULL" = true ]; then
    HELM_ARGS+=(--set image.pullPolicy=Always)
fi

# Add values file if specified
if [ -n "$VALUES_FILE" ]; then
    if [ ! -f "$VALUES_FILE" ]; then
        print_color $RED "❌ Values file not found: $VALUES_FILE"
        exit 1
    fi
    HELM_ARGS+=(-f "$VALUES_FILE")
    print_color $BLUE "📄 Using values file: $VALUES_FILE"
fi

# Execute Helm command
if [ "$DRY_RUN" = true ]; then
    print_color $YELLOW "🔧 Dry run - templating SharePoint MCP..."
    helm template "$RELEASE_NAME" "$CHART_PATH" "${HELM_ARGS[@]}"
elif [ "$UPGRADE" = true ]; then
    print_color $YELLOW "🔧 Upgrading SharePoint MCP..."
    helm upgrade "$RELEASE_NAME" "$CHART_PATH" "${HELM_ARGS[@]}"
else
    print_color $YELLOW "🔧 Installing SharePoint MCP..."
    helm install "$RELEASE_NAME" "$CHART_PATH" "${HELM_ARGS[@]}"
fi

if [ $? -eq 0 ] && [ "$DRY_RUN" = false ]; then
    if [ "$UPGRADE" = true ]; then
        print_color $GREEN "✅ Upgrade completed successfully!"
    else
        print_color $GREEN "✅ Installation completed successfully!"
    fi
    echo ""
    print_color $BLUE "🔗 To access the MCP server:"
    
    # Check which transport is being used by looking at values or using helm get
    TRANSPORT=$(helm get values "$RELEASE_NAME" --namespace "$NAMESPACE" -o json 2>/dev/null | grep -o '"transport":"[^"]*"' | cut -d'"' -f4 || echo "sse")
    
    if [ "$TRANSPORT" = "stdio" ]; then
        print_color $BLUE "📋 For stdio transport (kubectl exec):"
        echo "export POD_NAME=\$(kubectl get pods --namespace $NAMESPACE -l \"app.kubernetes.io/name=sharepoint-mcp,app.kubernetes.io/instance=$RELEASE_NAME\" -o jsonpath=\"{.items[0].metadata.name}\")"
        echo "kubectl exec -it \$POD_NAME --namespace $NAMESPACE -- python mcp_sharepoint/server.py"
    else
        print_color $BLUE "📋 For HTTP transport ($TRANSPORT):"
        echo "kubectl --namespace $NAMESPACE port-forward service/$RELEASE_NAME-sharepoint-mcp 8080:8000"
        echo "Then access: http://localhost:8080"
        echo ""
        print_color $BLUE "📖 For LibreChat integration:"
        echo "mcpServers:"
        echo "  sharepoint-mcp:"
        echo "    type: \"streamable-http\""
        echo "    url: \"http://$RELEASE_NAME-sharepoint-mcp.$NAMESPACE.svc.cluster.local:8000\""
        echo "    timeout: 30000"
        echo ""
        print_color $BLUE "📖 Or for external access via port-forward:"
        echo "mcpServers:"
        echo "  sharepoint-mcp:"
        echo "    type: \"streamable-http\""
        echo "    url: \"http://localhost:8080\""
        echo "    timeout: 30000"
    fi
    
    echo ""
    print_color $YELLOW "📊 To check the deployment status, run:"
    echo "kubectl get pods --namespace $NAMESPACE -l app.kubernetes.io/name=sharepoint-mcp"
    echo "kubectl logs --namespace $NAMESPACE -l app.kubernetes.io/name=sharepoint-mcp -f"
    echo ""
    print_color $YELLOW "🔧 To manage the deployment:"
    echo "# View current values:"
    echo "helm get values $RELEASE_NAME -n $NAMESPACE"
    echo ""
    echo "# Upgrade with new image:"
    echo "$0 --upgrade --image-tag=v0.2.4"
    echo ""
    echo "# Uninstall:"
    echo "helm uninstall $RELEASE_NAME -n $NAMESPACE"
    
elif [ "$DRY_RUN" = true ]; then
    print_color $GREEN "✅ Dry run completed successfully!"
    echo ""
    print_color $BLUE "💡 To actually install, run the same command without --dry-run"
else
    print_color $RED "❌ Operation failed!"
    echo ""
    print_color $YELLOW "🔍 Troubleshooting tips:"
    echo "1. Check if the release already exists: helm list -n $NAMESPACE"
    echo "2. Check pod status: kubectl get pods -n $NAMESPACE"
    echo "3. Check logs: kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=sharepoint-mcp"
    exit 1
fi
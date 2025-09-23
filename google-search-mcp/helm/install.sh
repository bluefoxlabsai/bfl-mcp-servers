#!/bin/bash

# Google Search MCP Helm Chart Installation Script
#
# Usage:
#   ./install.sh [release-name] [options]
#
# Environment Variables:
#   GOOGLE_API_KEY - Your Google API key (optional, will prompt if not set)
#   GOOGLE_CSE_ID  - Your Google Custom Search Engine ID (optional, will prompt if not set)
#   NAMESPACE      - Kubernetes namespace (optional, will prompt if not set, defaults to 'mcp-servers')
#
# Examples:
#   ./install.sh                              # Install with default release name and prompts
#   ./install.sh my-google-search-mcp         # Install with custom release name
#   GOOGLE_API_KEY=xyz ./install.sh           # Install with pre-set API key
#   NAMESPACE=google ./install.sh             # Install in 'google' namespace
#   ./install.sh --upgrade                    # Upgrade existing installation
#   ./install.sh --image-tag=v1.0.0          # Install with specific image tag
#   ./install.sh -f values-prod.yaml          # Install with custom values file
#   ./install.sh --server-type=enhanced       # Install with enhanced server (default)
#   ./install.sh --transport=sse              # Install with SSE transport

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

print_color $BLUE "🔍 Google Search MCP Helm Chart Installer"
echo ""

# Initialize variables
DRY_RUN=false
RELEASE_NAME=""
UPGRADE=false
IMAGE_TAG="latest"
VALUES_FILE=""
FORCE_PULL=false
SERVER_TYPE="enhanced"
TRANSPORT="sse"

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
        --server-type=*)
            SERVER_TYPE="${1#*=}"
            shift
            ;;
        --server-type)
            SERVER_TYPE="$2"
            shift 2
            ;;
        --transport=*)
            TRANSPORT="${1#*=}"
            shift
            ;;
        --transport)
            TRANSPORT="$2"
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
            echo "  --dry-run              Perform a dry run (template only, no actual installation)"
            echo "  --upgrade              Upgrade existing installation instead of install"
            echo "  --image-tag=TAG        Specify Docker image tag (default: latest)"
            echo "  --server-type=TYPE     Server type: enhanced|basic (default: enhanced)"
            echo "  --transport=TYPE       Transport: sse|streamable-http|stdio (default: sse)"
            echo "  --force-pull           Force pull latest image (sets pullPolicy=Always)"
            echo "  -f, --values FILE      Specify custom values file"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  GOOGLE_API_KEY - Your Google API key"
            echo "  GOOGLE_CSE_ID  - Your Google Custom Search Engine ID"
            echo "  NAMESPACE      - Kubernetes namespace (defaults to 'mcp-servers')"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Basic installation with enhanced server"
            echo "  $0 --upgrade --image-tag=v1.0.0      # Upgrade to specific version"
            echo "  $0 -f examples/values-prod.yaml       # Install with production config"
            echo "  $0 --server-type=basic                # Install basic server"
            echo "  $0 --transport=streamable-http        # Install with HTTP transport"
            echo "  $0 --force-pull                       # Force pull latest image"
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

# Validate server type
if [[ "$SERVER_TYPE" != "enhanced" && "$SERVER_TYPE" != "basic" ]]; then
    print_color $RED "❌ Invalid server type: $SERVER_TYPE. Must be 'enhanced' or 'basic'"
    exit 1
fi

# Validate transport
if [[ "$TRANSPORT" != "sse" && "$TRANSPORT" != "streamable-http" && "$TRANSPORT" != "stdio" ]]; then
    print_color $RED "❌ Invalid transport: $TRANSPORT. Must be 'sse', 'streamable-http', or 'stdio'"
    exit 1
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
print_color $PURPLE "🚀 Server type: $SERVER_TYPE"
print_color $PURPLE "📡 Transport: $TRANSPORT"

# Determine the chart path based on where the script is run from
if [ -f "Chart.yaml" ]; then
    CHART_PATH="."
elif [ -f "helm/Chart.yaml" ]; then
    CHART_PATH="./helm"
else
    print_color $RED "❌ Cannot find Chart.yaml. Please run this script from the project root or helm directory."
    exit 1
fi

# Get Google API key from user if not provided via environment
if [ -z "$GOOGLE_API_KEY" ]; then
    echo ""
    print_color $YELLOW "📋 Google API key (optional - can be configured later):"
    print_color $CYAN "   Press Enter to skip, or enter your Google API key:"
    read -s GOOGLE_API_KEY
    echo ""
fi

# Use placeholder if no API key provided
if [ -z "$GOOGLE_API_KEY" ]; then
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
    print_color $YELLOW "⚠️  API key not provided - using placeholder. Configure via secret after installation."
fi

# Get Google CSE ID from user if not provided via environment
if [ -z "$GOOGLE_CSE_ID" ]; then
    echo ""
    print_color $YELLOW "📋 Google Custom Search Engine ID (optional - can be configured later):"
    print_color $CYAN "   Press Enter to skip, or enter your Google CSE ID:"
    read GOOGLE_CSE_ID
    echo ""
fi

# Use placeholder if no CSE ID provided
if [ -z "$GOOGLE_CSE_ID" ]; then
    GOOGLE_CSE_ID="YOUR_GOOGLE_CSE_ID_HERE"
    print_color $YELLOW "⚠️  CSE ID not provided - using placeholder. Configure via secret after installation."
fi

# Build Helm command arguments
HELM_ARGS=(
    --namespace "$NAMESPACE"
    --set secret.googleApiKey="$GOOGLE_API_KEY"
    --set secret.googleCseId="$GOOGLE_CSE_ID"
    --set image.tag="$IMAGE_TAG"
    --set mcp.serverType="$SERVER_TYPE"
    --set mcp.transport="$TRANSPORT"
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
    print_color $YELLOW "🔧 Dry run - templating Google Search MCP..."
    helm template "$RELEASE_NAME" "$CHART_PATH" "${HELM_ARGS[@]}"
elif [ "$UPGRADE" = true ]; then
    print_color $YELLOW "🔧 Upgrading Google Search MCP..."
    helm upgrade "$RELEASE_NAME" "$CHART_PATH" "${HELM_ARGS[@]}"
else
    print_color $YELLOW "🔧 Installing Google Search MCP..."
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
    
    if [ "$TRANSPORT" = "stdio" ]; then
        print_color $BLUE "📋 For stdio transport (kubectl exec):"
        echo "export POD_NAME=\$(kubectl get pods --namespace $NAMESPACE -l \"app.kubernetes.io/name=google-search-mcp,app.kubernetes.io/instance=$RELEASE_NAME\" -o jsonpath=\"{.items[0].metadata.name}\")"
        if [ "$SERVER_TYPE" = "enhanced" ]; then
            echo "kubectl exec -it \$POD_NAME --namespace $NAMESPACE -- python enhanced_google_search_server.py"
        else
            echo "kubectl exec -it \$POD_NAME --namespace $NAMESPACE -- python google_search_mcp_server.py"
        fi
    else
        print_color $BLUE "📋 For HTTP transport ($TRANSPORT):"
        echo "kubectl --namespace $NAMESPACE port-forward service/$RELEASE_NAME-google-search-mcp 8080:8000"
        echo "Then access: http://localhost:8080"
        echo ""
        print_color $BLUE "📖 For LibreChat integration:"
        echo "mcpServers:"
        echo "  google-search-mcp:"
        echo "    type: \"$TRANSPORT\""
        echo "    url: \"http://$RELEASE_NAME-google-search-mcp.$NAMESPACE.svc.cluster.local:8000\""
        echo "    timeout: 30000"
        echo ""
        print_color $BLUE "📖 Or for external access via port-forward:"
        echo "mcpServers:"
        echo "  google-search-mcp:"
        echo "    type: \"$TRANSPORT\""
        echo "    url: \"http://localhost:8080\""
        echo "    timeout: 30000"
    fi
    
    if [ "$SERVER_TYPE" = "enhanced" ]; then
        echo ""
        print_color $GREEN "🚀 Enhanced server features available:"
        echo "  • search_google: Comprehensive web search with pagination and localization"
        echo "  • search_images: Image search with size/type filters"
        echo "  • search_by_date_range: Date-filtered search"
        echo "  • search_site_specific: Site-restricted search"
        echo "  • search_file_type: File type search (PDF, DOC, etc.)"
        echo "  • search_related: Find related pages"
        echo "  • search_cached: Get cached page versions"
        echo "  • get_search_suggestions: Get search suggestions"
        echo "  • get_api_status: Check API configuration and quota"
    else
        echo ""
        print_color $GREEN "🔍 Basic server features available:"
        echo "  • search_google: Basic Google search"
    fi
    
    echo ""
    print_color $YELLOW "📊 To check the deployment status, run:"
    echo "kubectl get pods --namespace $NAMESPACE -l app.kubernetes.io/name=google-search-mcp"
    echo "kubectl logs --namespace $NAMESPACE -l app.kubernetes.io/name=google-search-mcp -f"
    echo ""
    
    # Show API key configuration instructions if placeholders were used
    if [ "$GOOGLE_API_KEY" = "YOUR_GOOGLE_API_KEY_HERE" ] || [ "$GOOGLE_CSE_ID" = "YOUR_GOOGLE_CSE_ID_HERE" ]; then
        print_color $YELLOW "🔑 To configure API credentials later, update the secret:"
        echo "kubectl patch secret $RELEASE_NAME-secret -n $NAMESPACE --patch='"'{\"data\":{\"google-api-key\":\"'$(echo -n "YOUR_ACTUAL_API_KEY" | base64)'\",\"google-cse-id\":\"'$(echo -n "YOUR_ACTUAL_CSE_ID" | base64)'\"}}'\"
        echo ""
        print_color $CYAN "💡 Or update via Helm:"
        echo "helm upgrade $RELEASE_NAME $CHART_PATH -n $NAMESPACE \\"
        echo "  --set secret.googleApiKey=\"YOUR_ACTUAL_API_KEY\" \\"
        echo "  --set secret.googleCseId=\"YOUR_ACTUAL_CSE_ID\""
        echo ""
    fi
    print_color $YELLOW "🔧 To manage the deployment:"
    echo "# View current values:"
    echo "helm get values $RELEASE_NAME -n $NAMESPACE"
    echo ""
    echo "# Upgrade with new image:"
    echo "$0 --upgrade --image-tag=v1.0.1"
    echo ""
    echo "# Switch to enhanced server:"
    echo "$0 --upgrade --server-type=enhanced"
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
    echo "3. Check logs: kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=google-search-mcp"
    exit 1
fi
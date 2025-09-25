#!/bin/bash

# AccuWeather MCP Server Helm Chart Installation Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_color() {
    printf "${1}${2}${NC}\n"
}

print_color $BLUE "🌤️ AccuWeather MCP Server Helm Chart Installer"
echo ""

# Initialize variables
DRY_RUN=false
RELEASE_NAME=""
UPGRADE=false
IMAGE_TAG="latest"
VALUES_FILE=""
FORCE_PULL=false
TRANSPORT="sse"
ENABLE_SERVICE=false

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
        --force-pull)
            FORCE_PULL=true
            shift
            ;;
        --transport=*)
            TRANSPORT="${1#*=}"
            shift
            ;;
        --enable-service)
            ENABLE_SERVICE=true
            shift
            ;;
        -f)
            VALUES_FILE="$2"
            shift 2
            ;;
        --values=*)
            VALUES_FILE="${1#*=}"
            shift
            ;;
        -h|--help)
            cat << EOF
AccuWeather MCP Server Helm Chart Installation Script

Usage:
    $0 [release-name] [options]

Arguments:
    release-name    Name for the Helm release (optional, defaults to 'accuweather-mcp')

Options:
    --dry-run              Show what would be installed without actually installing
    --upgrade              Upgrade an existing installation
    --image-tag=TAG        Specify the Docker image tag (default: latest)
    --force-pull           Force pull the Docker image even if it exists locally
    --transport=MODE       Set transport mode: stdio, sse, or http (default: sse)
    --enable-service       Force enable Kubernetes service (auto-enabled for sse/http transport)
    -f, --values=FILE      Specify a custom values file
    -h, --help             Show this help message

Environment Variables:
    ACCUWEATHER_API_KEY    Your AccuWeather API key (required)
    NAMESPACE              Kubernetes namespace (default: mcp-servers)

Examples:
    $0                                    # Basic installation with prompts
    $0 my-weather-server                  # Install with custom release name
    $0 --transport=sse                    # Install with SSE transport
    $0 --upgrade                          # Upgrade existing installation
    $0 -f examples/values-prod.yaml       # Install with production values
    ACCUWEATHER_API_KEY=your-key $0       # Install with pre-set API key

For more information, visit:
https://github.com/bluefoxlabsai/bfl-mcp-servers/tree/main/accuweather-mcp/helm
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
    RELEASE_NAME="accuweather-mcp"
fi

# Validate transport mode
if [[ "$TRANSPORT" != "stdio" && "$TRANSPORT" != "http" && "$TRANSPORT" != "sse" ]]; then
    print_color $RED "❌ Invalid transport mode: $TRANSPORT"
    print_color $YELLOW "Valid options: stdio, sse, http"
    exit 1
fi

# Auto-enable service for HTTP and SSE transports
if [[ "$TRANSPORT" == "http" || "$TRANSPORT" == "sse" ]]; then
    ENABLE_SERVICE=true
fi

print_color $PURPLE "📋 Configuration Summary:"
echo "  Release Name: $RELEASE_NAME"
echo "  Transport: $TRANSPORT"
echo "  Image Tag: $IMAGE_TAG"
echo "  Enable Service: $ENABLE_SERVICE"
echo "  Dry Run: $DRY_RUN"
echo "  Upgrade: $UPGRADE"
if [[ -n "$VALUES_FILE" ]]; then
    echo "  Values File: $VALUES_FILE"
fi
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
    read -p "Enter the namespace to install to (default: mcp-servers): " NAMESPACE
    NAMESPACE=${NAMESPACE:-mcp-servers}
fi

print_color $GREEN "✅ Using namespace: $NAMESPACE"

# Create namespace if it doesn't exist
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_color $YELLOW "📁 Creating namespace: $NAMESPACE"
    if [[ "$DRY_RUN" == "false" ]]; then
        kubectl create namespace "$NAMESPACE"
    else
        print_color $BLUE "   (dry-run) Would create namespace: $NAMESPACE"
    fi
else
    print_color $GREEN "✅ Namespace already exists: $NAMESPACE"
fi

# Get AccuWeather API key if not set
if [[ -z "$ACCUWEATHER_API_KEY" ]]; then
    echo ""
    print_color $BLUE "🔑 AccuWeather API Key Configuration"
    print_color $YELLOW "You need an AccuWeather API key from: https://developer.accuweather.com/"
    print_color $YELLOW "Sign up for free and create an app to get your API key"
    echo ""
    read -sp "Enter your AccuWeather API Key: " ACCUWEATHER_API_KEY
    echo ""
fi

# Validate API key (basic format check)
if [[ -z "$ACCUWEATHER_API_KEY" ]]; then
    print_color $RED "❌ AccuWeather API key is required"
    exit 1
fi

print_color $GREEN "✅ AccuWeather API key configured"

# Build Helm command
HELM_CMD="helm"
if [[ "$UPGRADE" == "true" ]]; then
    HELM_CMD="$HELM_CMD upgrade"
else
    HELM_CMD="$HELM_CMD install"
fi

HELM_CMD="$HELM_CMD $RELEASE_NAME ."
HELM_CMD="$HELM_CMD --namespace $NAMESPACE"

if [[ "$UPGRADE" == "false" ]]; then
    HELM_CMD="$HELM_CMD --create-namespace"
fi

# Add values
HELM_CMD="$HELM_CMD --set accuweather.apiKey=$ACCUWEATHER_API_KEY"
HELM_CMD="$HELM_CMD --set mcp.transport=$TRANSPORT"
HELM_CMD="$HELM_CMD --set image.tag=$IMAGE_TAG"

if [[ "$ENABLE_SERVICE" == "true" ]]; then
    HELM_CMD="$HELM_CMD --set service.enabled=\"true\""
fi

if [[ "$FORCE_PULL" == "true" ]]; then
    HELM_CMD="$HELM_CMD --set image.pullPolicy=Always"
fi

# Add custom values file if provided
if [[ -n "$VALUES_FILE" ]]; then
    if [[ ! -f "$VALUES_FILE" ]]; then
        print_color $RED "❌ Values file not found: $VALUES_FILE"
        exit 1
    fi
    HELM_CMD="$HELM_CMD --values $VALUES_FILE"
fi

# Add dry-run flag if requested
if [[ "$DRY_RUN" == "true" ]]; then
    HELM_CMD="$HELM_CMD --dry-run --debug"
fi

# Show final configuration
echo ""
print_color $PURPLE "🎯 Final Configuration:"
echo "  Release Name: $RELEASE_NAME"
echo "  Namespace: $NAMESPACE"
echo "  Transport: $TRANSPORT"
echo "  Image Tag: $IMAGE_TAG"
echo "  Service Enabled: $ENABLE_SERVICE"
echo "  API Key: ***configured***"
if [[ -n "$VALUES_FILE" ]]; then
    echo "  Values File: $VALUES_FILE"
fi
echo ""

# Ask for confirmation unless it's a dry run
if [[ "$DRY_RUN" == "false" ]]; then
    read -p "Do you want to proceed with the installation? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_color $YELLOW "🚫 Installation cancelled"
        exit 0
    fi
fi

# Execute Helm command
echo ""
if [[ "$DRY_RUN" == "true" ]]; then
    print_color $BLUE "🔍 Running dry-run validation..."
else
    if [[ "$UPGRADE" == "true" ]]; then
        print_color $BLUE "⬆️  Upgrading AccuWeather MCP Server..."
    else
        print_color $BLUE "🚀 Installing AccuWeather MCP Server..."
    fi
fi

echo ""
print_color $YELLOW "Executing: $HELM_CMD"
echo ""

# Execute the command
if eval "$HELM_CMD"; then
    if [[ "$DRY_RUN" == "true" ]]; then
        print_color $GREEN "✅ Dry-run validation completed successfully!"
        print_color $YELLOW "Remove --dry-run flag to perform actual installation"
    else
        echo ""
        print_color $GREEN "🎉 AccuWeather MCP Server installed successfully!"
        echo ""
        print_color $BLUE "📋 Next steps:"
        if [[ "$TRANSPORT" == "stdio" ]]; then
            echo "  1. Connect to the server via kubectl exec:"
            echo "     kubectl exec -it -n $NAMESPACE deployment/$RELEASE_NAME -- uv run mcp-accuweather"
        elif [[ "$TRANSPORT" == "sse" ]]; then
            echo "  1. Check service status:"
            echo "     kubectl get service -n $NAMESPACE $RELEASE_NAME"
            echo "  2. Port forward to access the SSE server:"
            echo "     kubectl port-forward -n $NAMESPACE service/$RELEASE_NAME 8000:8000"
            echo "  3. SSE endpoint will be available at: http://localhost:8000/sse"
            echo "  4. Health check at: http://localhost:8000/health"
        else
            echo "  1. Check service status:"
            echo "     kubectl get service -n $NAMESPACE $RELEASE_NAME"
            echo "  2. Port forward to access the server:"
            echo "     kubectl port-forward -n $NAMESPACE service/$RELEASE_NAME 8000:8000"
        fi
        echo ""
        echo "  📚 Documentation: https://github.com/bluefoxlabsai/bfl-mcp-servers/tree/main/accuweather-mcp"
        echo "  🐛 Issues: https://github.com/bluefoxlabsai/bfl-mcp-servers/issues"
    fi
else
    print_color $RED "❌ Installation failed!"
    echo ""
    print_color $YELLOW "💡 Troubleshooting tips:"
    echo "  1. Check if the namespace exists and you have permissions"
    echo "  2. Verify your AccuWeather API key is correct"
    echo "  3. Check Helm and kubectl versions are compatible"
    echo "  4. Run with --dry-run flag to validate configuration"
    echo ""
    exit 1
fi
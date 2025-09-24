#!/bin/bash

# Slack MCP Server Helm Chart Installation Script
#
# Usage:
#   ./install.sh [release-name] [options]
#
# Environment Variables:
#   SLACK_BOT_TOKEN  - Your Slack Bot OAuth Token (optional, will prompt if not set)
#   SLACK_USER_TOKEN - Your Slack User OAuth Token (optional, will prompt if not set)
#   NAMESPACE        - Kubernetes namespace (optional, will prompt if not set, defaults to 'mcp-servers')
#
# Examples:
#   ./install.sh                                    # Install with default release name and prompts
#   ./install.sh my-slack-mcp                       # Install with custom release name
#   SLACK_BOT_TOKEN=xoxb-xxx ./install.sh           # Install with pre-set bot token
#   NAMESPACE=slack ./install.sh                    # Install in 'slack' namespace
#   ./install.sh --upgrade                          # Upgrade existing installation
#   ./install.sh --image-tag=v0.1.4                # Install with specific image tag
#   ./install.sh -f values-prod.yaml                # Install with custom values file
#   ./install.sh --transport=http                   # Install with HTTP transport

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

print_color $BLUE "🚀 Slack MCP Server Helm Chart Installer"
echo ""

# Initialize variables
DRY_RUN=false
RELEASE_NAME=""
UPGRADE=false
IMAGE_TAG="latest"
VALUES_FILE=""
FORCE_PULL=false
TRANSPORT="stdio"
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
Slack MCP Server Helm Chart Installation Script

Usage:
    $0 [release-name] [options]

Arguments:
    release-name    Name for the Helm release (optional, defaults to 'slack-mcp-server')

Options:
    --dry-run              Show what would be installed without actually installing
    --upgrade              Upgrade an existing installation
    --image-tag=TAG        Specify the Docker image tag (default: latest)
    --force-pull           Force pull the Docker image even if it exists locally
    --transport=MODE       Set transport mode: stdio or http (default: stdio)
    --enable-service       Force enable Kubernetes service (auto-enabled for http transport)
    -f, --values=FILE      Specify a custom values file
    -h, --help             Show this help message

Environment Variables:
    SLACK_BOT_TOKEN        Your Slack Bot User OAuth Token (xoxb-...)
    SLACK_USER_TOKEN       Your Slack User OAuth Token (xoxp-...)
    NAMESPACE              Kubernetes namespace (default: mcp-servers)

Examples:
    $0                                    # Basic installation with prompts
    $0 my-slack-server                    # Install with custom release name
    $0 --transport=http                   # Install with HTTP transport
    $0 --upgrade                          # Upgrade existing installation
    $0 -f examples/values-prod.yaml       # Install with production values
    SLACK_BOT_TOKEN=xoxb-xxx $0           # Install with pre-set token

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
    RELEASE_NAME="slack-mcp-server"
fi

# Validate transport mode
if [[ "$TRANSPORT" != "stdio" && "$TRANSPORT" != "http" ]]; then
    print_color $RED "❌ Invalid transport mode: $TRANSPORT"
    print_color $YELLOW "Valid options: stdio, http"
    exit 1
fi

# Auto-enable service for HTTP transport
if [[ "$TRANSPORT" == "http" ]]; then
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

# Get Slack tokens if not set
if [[ -z "$SLACK_BOT_TOKEN" ]]; then
    echo ""
    print_color $BLUE "🔑 Slack Bot Token Configuration"
    print_color $YELLOW "You need a Slack Bot User OAuth Token (starts with xoxb-)"
    print_color $YELLOW "Get it from: https://api.slack.com/apps -> Your App -> OAuth & Permissions"
    echo ""
    read -sp "Enter your Slack Bot Token (xoxb-...): " SLACK_BOT_TOKEN
    echo ""
fi

if [[ -z "$SLACK_USER_TOKEN" ]]; then
    echo ""
    print_color $BLUE "🔑 Slack User Token Configuration"
    print_color $YELLOW "You need a Slack User OAuth Token (starts with xoxp-) for search features"
    print_color $YELLOW "Get it from: https://api.slack.com/apps -> Your App -> OAuth & Permissions"
    echo ""
    read -sp "Enter your Slack User Token (xoxp-...): " SLACK_USER_TOKEN
    echo ""
fi

# Validate tokens
if [[ ! "$SLACK_BOT_TOKEN" =~ ^xoxb- ]]; then
    print_color $RED "❌ Invalid Slack Bot Token format. Should start with 'xoxb-'"
    exit 1
fi

if [[ ! "$SLACK_USER_TOKEN" =~ ^xoxp- ]]; then
    print_color $RED "❌ Invalid Slack User Token format. Should start with 'xoxp-'"
    exit 1
fi

print_color $GREEN "✅ Slack tokens validated"

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
HELM_CMD="$HELM_CMD --set slack.botToken=$SLACK_BOT_TOKEN"
HELM_CMD="$HELM_CMD --set slack.userToken=$SLACK_USER_TOKEN"
HELM_CMD="$HELM_CMD --set mcp.transport=$TRANSPORT"
HELM_CMD="$HELM_CMD --set image.tag=$IMAGE_TAG"

if [[ "$ENABLE_SERVICE" == "true" ]]; then
    HELM_CMD="$HELM_CMD --set service.enabled=true"
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
echo "  Bot Token: xoxb-***"
echo "  User Token: xoxp-***"
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
        print_color $BLUE "⬆️  Upgrading Slack MCP Server..."
    else
        print_color $BLUE "🚀 Installing Slack MCP Server..."
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
        print_color $GREEN "🎉 Slack MCP Server installed successfully!"
        echo ""
        print_color $BLUE "📋 Next steps:"
        if [[ "$TRANSPORT" == "stdio" ]]; then
            echo "  1. Connect to the server via kubectl exec:"
            echo "     kubectl exec -it -n $NAMESPACE deployment/$RELEASE_NAME -- uv run slack-mcp-server"
        else
            echo "  1. Check service status:"
            echo "     kubectl get service -n $NAMESPACE $RELEASE_NAME"
            echo "  2. Port forward to access the server:"
            echo "     kubectl port-forward -n $NAMESPACE service/$RELEASE_NAME 8000:8000"
        fi
        echo ""
        echo "  📚 Documentation: https://github.com/bluefoxlabsai/bfl-mcp-servers/tree/main/slack-server-mcp"
        echo "  🐛 Issues: https://github.com/bluefoxlabsai/bfl-mcp-servers/issues"
    fi
else
    print_color $RED "❌ Installation failed!"
    echo ""
    print_color $YELLOW "💡 Troubleshooting tips:"
    echo "  1. Check if the namespace exists and you have permissions"
    echo "  2. Verify your Slack tokens are correct"
    echo "  3. Check Helm and kubectl versions are compatible"
    echo "  4. Run with --dry-run flag to validate configuration"
    echo ""
    exit 1
fi
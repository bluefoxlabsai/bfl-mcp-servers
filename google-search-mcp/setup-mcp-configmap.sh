#!/bin/bash

# Google Search MCP Server - ConfigMap Setup Script
# This script sets up the MCP server to use credentials from a Kubernetes ConfigMap

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Google Search MCP Server - ConfigMap Setup${NC}"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

if ! command_exists kubectl; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
    exit 1
fi

if ! command_exists helm; then
    echo -e "${RED}❌ helm not found. Please install Helm 3.x first.${NC}"
    exit 1
fi

# Check if we can connect to Kubernetes
if ! kubectl cluster-info >/dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Get namespace
NAMESPACE=${1:-"mcp-servers"}
RELEASE_NAME=${2:-"mcp-google-search"}
CONFIGMAP_NAME="google-search-credentials"

echo -e "\n${YELLOW}🏷️  Configuration:${NC}"
echo "   Namespace: ${NAMESPACE}"
echo "   Release Name: ${RELEASE_NAME}"
echo "   ConfigMap Name: ${CONFIGMAP_NAME}"

# Check environment variables
echo -e "\n${YELLOW}🔑 Checking environment variables...${NC}"

if [[ -z "$GOOGLE_API_KEY" ]]; then
    echo -e "${RED}❌ GOOGLE_API_KEY environment variable is not set${NC}"
    echo "   Please set it with: export GOOGLE_API_KEY=\"your_api_key\""
    exit 1
fi

if [[ -z "$GOOGLE_CSE_ID" ]]; then
    echo -e "${RED}❌ GOOGLE_CSE_ID environment variable is not set${NC}"
    echo "   Please set it with: export GOOGLE_CSE_ID=\"your_cse_id\""
    exit 1
fi

echo -e "${GREEN}✅ Environment variables are set${NC}"
echo "   GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:10}..."
echo "   GOOGLE_CSE_ID: ${GOOGLE_CSE_ID}"

# Create namespace if it doesn't exist
echo -e "\n${YELLOW}🏗️  Creating namespace if needed...${NC}"
if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Namespace '$NAMESPACE' already exists${NC}"
else
    kubectl create namespace "$NAMESPACE"
    echo -e "${GREEN}✅ Created namespace: $NAMESPACE${NC}"
fi

# Create or update ConfigMap
echo -e "\n${YELLOW}📄 Creating/updating ConfigMap...${NC}"
kubectl create configmap "$CONFIGMAP_NAME" \
    --from-literal=GOOGLE_API_KEY="$GOOGLE_API_KEY" \
    --from-literal=GOOGLE_CSE_ID="$GOOGLE_CSE_ID" \
    --namespace="$NAMESPACE" \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✅ ConfigMap '$CONFIGMAP_NAME' created/updated in namespace '$NAMESPACE'${NC}"

# Deploy or upgrade Helm chart
echo -e "\n${YELLOW}🚀 Deploying Helm chart...${NC}"
cd "$(dirname "$0")/helm"

helm upgrade --install "$RELEASE_NAME" . \
    --namespace="$NAMESPACE" \
    --set secret.useEnvVars=true \
    --set secret.externalConfigMap="$CONFIGMAP_NAME" \
    --set mcp.transport=sse \
    --set mcp.serverType=enhanced \
    --wait

echo -e "${GREEN}✅ Helm chart deployed successfully!${NC}"

# Get service information
echo -e "\n${YELLOW}📡 Getting service information...${NC}"
SERVICE_NAME=$(kubectl get service -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME" -o jsonpath='{.items[0].metadata.name}')
SERVICE_URL="http://${SERVICE_NAME}.${NAMESPACE}.svc.cluster.local:8000/sse"

echo -e "${GREEN}✅ Service deployed:${NC}"
echo "   Service Name: $SERVICE_NAME"
echo "   Internal URL: $SERVICE_URL"

# Verify deployment
echo -e "\n${YELLOW}🔍 Verifying deployment...${NC}"

# Check if pods are running
POD_NAME=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [[ -n "$POD_NAME" ]]; then
    echo -e "${GREEN}✅ Pod is running: $POD_NAME${NC}"
    
    # Check environment variables in pod
    echo -e "\n${YELLOW}🔧 Checking environment variables in pod...${NC}"
    ENV_CHECK=$(kubectl exec -n "$NAMESPACE" "$POD_NAME" -- env | grep GOOGLE || echo "")
    if [[ -n "$ENV_CHECK" ]]; then
        echo -e "${GREEN}✅ Environment variables are set in pod:${NC}"
        echo "$ENV_CHECK" | sed 's/^/   /'
    else
        echo -e "${RED}❌ Environment variables not found in pod${NC}"
    fi
    
    # Check pod logs
    echo -e "\n${YELLOW}📝 Recent pod logs:${NC}"
    kubectl logs -n "$NAMESPACE" "$POD_NAME" --tail=10 || echo "   No logs available yet"
else
    echo -e "${RED}❌ Pod not found or not running${NC}"
fi

# Show ConfigMap contents (masked)
echo -e "\n${YELLOW}📄 ConfigMap contents (masked):${NC}"
kubectl get configmap -n "$NAMESPACE" "$CONFIGMAP_NAME" -o jsonpath='{.data}' | \
    sed 's/"GOOGLE_API_KEY":"[^"]*"/"GOOGLE_API_KEY":"***masked***"/g' | \
    sed 's/^/   /'

echo -e "\n${GREEN}🎉 Setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "   • ConfigMap '$CONFIGMAP_NAME' created with your API credentials"
echo "   • Helm chart '$RELEASE_NAME' deployed in namespace '$NAMESPACE'"
echo "   • Server configured to use environment variables from ConfigMap"
echo "   • Service URL: $SERVICE_URL"
echo ""
echo -e "${BLUE}🔗 MCP Client Configuration:${NC}"
echo "   Use this URL in your MCP client: $SERVICE_URL"
echo ""
echo -e "${BLUE}🛠️  Useful commands:${NC}"
echo "   • Check pods: kubectl get pods -n $NAMESPACE -l app.kubernetes.io/instance=$RELEASE_NAME"
echo "   • View logs: kubectl logs -n $NAMESPACE -l app.kubernetes.io/instance=$RELEASE_NAME"
echo "   • Port forward: kubectl port-forward -n $NAMESPACE svc/$SERVICE_NAME 8000:8000"
echo "   • Delete: helm uninstall $RELEASE_NAME -n $NAMESPACE"
echo ""
echo -e "${GREEN}✅ Your Google Search MCP server is ready for use!${NC}"
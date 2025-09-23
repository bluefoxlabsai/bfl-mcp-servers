# Google Search MCP - ConfigMap Setup for MCP Client Integration

This guide shows how to set up the Google Search MCP server to use credentials from a ConfigMap, perfect for MCP client integration.

## Problem

Your MCP client config sets environment variables:
```yaml
env:
  GOOGLE_API_KEY: "${GOOGLE_API_KEY}"
  GOOGLE_SEARCH_API_KEY: "${GOOGLE_SEARCH_API_KEY}"  # Not used by server
  GOOGLE_CSE_ID: "${GOOGLE_CSE_ID}"
```

But these client-side environment variables don't automatically reach the Kubernetes pod.

## Solution Options

### Option 1: Create ConfigMap from Environment Variables (Recommended)

First, create a ConfigMap with your credentials:

```bash
# Create ConfigMap from your environment variables
kubectl create configmap google-search-credentials \
  --from-literal=GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
  --from-literal=GOOGLE_CSE_ID="${GOOGLE_CSE_ID}" \
  --namespace=mcp-servers
```

Then deploy the Helm chart to use this external ConfigMap:

```bash
helm install mcp-google-search ./helm \
  --namespace=mcp-servers \
  --set secret.useEnvVars=true \
  --set secret.externalConfigMap=google-search-credentials
```

### Option 2: Pass Values During Deployment

```bash
# Deploy with values directly
helm install mcp-google-search ./helm \
  --namespace=mcp-servers \
  --set secret.useEnvVars=true \
  --set-string secret.googleApiKey="${GOOGLE_API_KEY}" \
  --set-string secret.googleCseId="${GOOGLE_CSE_ID}"
```

### Option 3: Use the Install Script

```bash
# Set environment variables and use install script
export GOOGLE_API_KEY="your_key"
export GOOGLE_CSE_ID="your_cse_id"
cd helm
./install.sh mcp-google-search --use-env-vars
```

## Automated Setup Script

Create this script to automate the process:

```bash
#!/bin/bash
# setup-mcp-google-search.sh

# Ensure environment variables are set
if [[ -z "$GOOGLE_API_KEY" || -z "$GOOGLE_CSE_ID" ]]; then
  echo "Error: GOOGLE_API_KEY and GOOGLE_CSE_ID must be set"
  exit 1
fi

# Create namespace if it doesn't exist
kubectl create namespace mcp-servers --dry-run=client -o yaml | kubectl apply -f -

# Create or update ConfigMap
kubectl create configmap google-search-credentials \
  --from-literal=GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
  --from-literal=GOOGLE_CSE_ID="${GOOGLE_CSE_ID}" \
  --namespace=mcp-servers \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy Helm chart
helm upgrade --install mcp-google-search ./helm \
  --namespace=mcp-servers \
  --set secret.useEnvVars=true \
  --set secret.externalConfigMap=google-search-credentials

echo "Google Search MCP server deployed successfully!"
echo "Service URL: http://mcp-google-search-google-search-mcp.mcp-servers.svc.cluster.local:8000/sse"
```

Make it executable and run:
```bash
chmod +x setup-mcp-google-search.sh
./setup-mcp-google-search.sh
```

## MCP Client Configuration

Your MCP client config will work with the deployed server:

```yaml
# Kubernetes-hosted Google Search MCP server
google-search:
  type: sse
  url: 'http://mcp-google-search-google-search-mcp.mcp-servers.svc.cluster.local:8000/sse'
  timeout: 30000
  # Note: These env vars are for the MCP client, not the server
  # The server gets its credentials from the Kubernetes ConfigMap
  env:
    GOOGLE_API_KEY: "${GOOGLE_API_KEY}"
    GOOGLE_CSE_ID: "${GOOGLE_CSE_ID}"
  startup: true
  chatMenu: true
  iconPath: "/app/client/public/assets/search.svg"
  serverInstructions: |
    You are a web search assistant with access to Google Custom Search via a Kubernetes-hosted MCP server.
    You can perform targeted web searches and retrieve relevant information from across the internet.
    Use your search capabilities to find current information, news, research, and answers to user questions.
    Always cite the sources and URLs in your responses.
    Format search results in clear, readable markdown with proper attribution.
    If you cannot find relevant information, respond with "I don't know".
    Respect search result rankings and provide the most relevant information first.
```

**Important Notes:**
1. Remove `GOOGLE_SEARCH_API_KEY` from your MCP config - the server doesn't use it
2. The server gets credentials from Kubernetes ConfigMap, not from the MCP client env vars
3. The MCP client env vars are separate from the server's environment

## Verification

Check that everything is working:

```bash
# Check ConfigMap
kubectl get configmap google-search-credentials -n mcp-servers -o yaml

# Check pod environment
kubectl get pods -n mcp-servers -l app.kubernetes.io/name=google-search-mcp
kubectl exec -it <pod-name> -n mcp-servers -- env | grep GOOGLE

# Test the service
kubectl port-forward -n mcp-servers svc/mcp-google-search-google-search-mcp 8000:8000
# Then test: curl http://localhost:8000/sse
```
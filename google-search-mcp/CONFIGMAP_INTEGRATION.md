# MCP ConfigMap Integration Example

This document shows exactly how to integrate your MCP client configuration with the Kubernetes-hosted Google Search MCP server using ConfigMap injection.

## The Problem Solved

Your MCP client config sets environment variables that need to reach the Kubernetes pod:

```yaml
google-search:
  type: sse
  url: 'http://mcp-google-search-google-search-mcp.mcp-servers.svc.cluster.local:8000/sse'
  env:
    GOOGLE_API_KEY: "${GOOGLE_API_KEY}"
    GOOGLE_CSE_ID: "${GOOGLE_CSE_ID}"
```

**Issue**: These env vars are for the MCP client, but the server running in Kubernetes needs its own copy of these credentials.

## Solution: ConfigMap Environment Injection

### Step 1: Set Your Environment Variables

```bash
# Set your actual credentials
export GOOGLE_API_KEY="AIzaSyCH6vOfEjV2qfK8Hv4KzPwJyQnMjY_pXtQ"
export GOOGLE_CSE_ID="a60223a5eab474654"
```

### Step 2: Deploy Using ConfigMap Injection

#### Option A: Use the Automated Setup Script

```bash
cd /Users/Jay/Development/bfl-mcp-servers/google-search-mcp
./setup-mcp-configmap.sh mcp-servers mcp-google-search
```

#### Option B: Manual Steps

```bash
# 1. Create namespace
kubectl create namespace mcp-servers --dry-run=client -o yaml | kubectl apply -f -

# 2. Create ConfigMap with your credentials
kubectl create configmap google-search-credentials \
  --from-literal=GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
  --from-literal=GOOGLE_CSE_ID="${GOOGLE_CSE_ID}" \
  --namespace=mcp-servers \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Deploy Helm chart to use external ConfigMap
cd helm
helm upgrade --install mcp-google-search . \
  --namespace=mcp-servers \
  --set secret.useEnvVars=true \
  --set secret.externalConfigMap=google-search-credentials \
  --wait
```

### Step 3: Verify the Deployment

```bash
# Check the ConfigMap
kubectl get configmap google-search-credentials -n mcp-servers -o yaml

# Check pods are running
kubectl get pods -n mcp-servers -l app.kubernetes.io/name=google-search-mcp

# Verify environment variables in pod
POD_NAME=$(kubectl get pods -n mcp-servers -l app.kubernetes.io/name=google-search-mcp -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n mcp-servers $POD_NAME -- env | grep GOOGLE

# Check service
kubectl get service -n mcp-servers -l app.kubernetes.io/name=google-search-mcp
```

## How It Works

### ConfigMap Creation
The ConfigMap stores your credentials:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: google-search-credentials
  namespace: mcp-servers
data:
  GOOGLE_API_KEY: "AIzaSyCH6vOfEjV2qfK8Hv4KzPwJyQnMjY_pXtQ"
  GOOGLE_CSE_ID: "a60223a5eab474654"
```

### Deployment Configuration
The deployment template injects these as environment variables:
```yaml
# In deployment.yaml template
env:
  - name: GOOGLE_API_KEY
    valueFrom:
      configMapKeyRef:
        name: google-search-credentials
        key: GOOGLE_API_KEY
  - name: GOOGLE_CSE_ID
    valueFrom:
      configMapKeyRef:
        name: google-search-credentials
        key: GOOGLE_CSE_ID
```

### Helm Values
The key settings in values.yaml:
```yaml
secret:
  useEnvVars: true                           # Enable env var mode
  externalConfigMap: google-search-credentials  # Use external ConfigMap
```

## Testing the Integration

### Test 1: Port Forward and Direct Access
```bash
# Port forward the service
kubectl port-forward -n mcp-servers svc/mcp-google-search-google-search-mcp 8000:8000

# Test the SSE endpoint (in another terminal)
curl -N http://localhost:8000/sse
```

### Test 2: From Within Cluster
```bash
# Create a test pod
kubectl run test-client --image=curlimages/curl --rm -i --tty --restart=Never -- sh

# Inside the pod, test the service
curl -N http://mcp-google-search-google-search-mcp.mcp-servers.svc.cluster.local:8000/sse
```

### Test 3: Check Environment Variables
```bash
# Verify the server has the credentials
kubectl exec -n mcp-servers $POD_NAME -- python -c "
import os
print(f'GOOGLE_API_KEY: {os.environ.get(\"GOOGLE_API_KEY\", \"NOT_SET\")}')
print(f'GOOGLE_CSE_ID: {os.environ.get(\"GOOGLE_CSE_ID\", \"NOT_SET\")}')
"
```

## Your Final MCP Client Configuration

With the server deployed, your MCP client config can remain exactly as you had it:

```yaml
# Kubernetes-hosted Google Search MCP server
google-search:
  type: sse
  url: 'http://mcp-google-search-google-search-mcp.mcp-servers.svc.cluster.local:8000/sse'
  timeout: 30000
  env:
    GOOGLE_API_KEY: "${GOOGLE_API_KEY}"      # For MCP client use
    GOOGLE_CSE_ID: "${GOOGLE_CSE_ID}"        # For MCP client use
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

**Note**: Remove the `GOOGLE_SEARCH_API_KEY` line since the server doesn't use it.

## Credential Flow Summary

1. **Environment Variables** → Set on your local machine/CI system
2. **ConfigMap** → Created from environment variables, stored in Kubernetes
3. **Pod Environment** → Injected from ConfigMap into running containers
4. **MCP Server** → Reads credentials from its environment variables
5. **MCP Client** → Connects to server via Kubernetes service URL

This approach ensures your credentials are properly managed through Kubernetes while keeping them secure and separate from your application code.

## Cleanup

To remove everything:
```bash
# Remove Helm deployment
helm uninstall mcp-google-search -n mcp-servers

# Remove ConfigMap
kubectl delete configmap google-search-credentials -n mcp-servers

# Remove namespace (if desired)
kubectl delete namespace mcp-servers
```

## Security Notes

- ConfigMaps store data in base64 encoding, not encryption
- For production, consider using Kubernetes Secrets instead of ConfigMaps
- Use RBAC to limit access to the ConfigMap
- Consider using external secret management systems like HashiCorp Vault or AWS Secrets Manager
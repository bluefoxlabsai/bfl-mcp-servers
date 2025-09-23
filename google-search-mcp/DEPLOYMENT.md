# Google Search MCP Server - Deployment Guide

This guide covers different deployment methods for the Google Search MCP Server.

## Prerequisites

1. **Kubernetes cluster** with kubectl configured
2. **Helm 3.x** installed
3. **Google Custom Search Engine** setup:
   - API Key from Google Cloud Console
   - Custom Search Engine ID

## Deployment Methods

### Method 1: Environment Variables (Recommended for MCP Integration)

Use this method when you want to pass credentials through environment variables, perfect for MCP server implementations.

```bash
# Set your credentials as environment variables
export GOOGLE_API_KEY="your_actual_api_key"
export GOOGLE_CSE_ID="your_actual_cse_id"

# Install using environment variables
cd helm
./install.sh my-google-search --use-env-vars
```

**Advantages:**
- No secrets stored in Kubernetes
- Credentials passed directly from environment
- Perfect for MCP server integration
- More flexible for different environments

### Method 2: Kubernetes Secrets (Default)

Use this method for traditional Kubernetes deployments where you want credentials stored as secrets.

```bash
# Install using interactive prompts (will create Kubernetes secrets)
cd helm
./install.sh my-google-search

# You'll be prompted for:
# - API Key
# - CSE ID
```

**Advantages:**
- Credentials encrypted in Kubernetes
- Standard Kubernetes security practices
- Automatic base64 encoding
- Centralized secret management

### Method 3: Manual Helm Commands

For advanced users who want direct control over Helm values.

#### Using Environment Variables:
```bash
helm install my-google-search ./helm \
  --set secret.useEnvVars=true \
  --set-string secret.googleApiKey="$GOOGLE_API_KEY" \
  --set-string secret.googleCseId="$GOOGLE_CSE_ID"
```

#### Using Kubernetes Secrets:
```bash
helm install my-google-search ./helm \
  --set secret.useEnvVars=false \
  --set-string secret.googleApiKey="your_api_key" \
  --set-string secret.googleCseId="your_cse_id"
```

## Configuration Options

### Values.yaml Options

```yaml
# Credential management
secret:
  useEnvVars: false  # Set to true to use environment variables instead of secrets
  googleApiKey: ""   # Your Google API key
  googleCseId: ""    # Your Google Custom Search Engine ID

# Image configuration
image:
  repository: bfljerum/google-search-mcp
  tag: latest
  pullPolicy: IfNotPresent

# Server configuration
server:
  type: enhanced     # Use enhanced server with 9 tools
  transport: sse     # Server-Sent Events transport

# Resource limits
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi
```

### Environment Variables

When using `useEnvVars: true`, the following environment variables are expected:

- `GOOGLE_API_KEY`: Your Google Custom Search API key
- `GOOGLE_CSE_ID`: Your Google Custom Search Engine ID

## Testing Deployments

### Dry Run Test
```bash
# Test environment variable configuration
export GOOGLE_API_KEY="test_key"
export GOOGLE_CSE_ID="test_id"
./install.sh test-env --use-env-vars --dry-run

# Test secret-based configuration
./install.sh test-secret --dry-run
```

### Health Checks
```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=google-search-mcp

# Check logs
kubectl logs -l app.kubernetes.io/name=google-search-mcp

# Run Helm tests
helm test my-google-search
```

## Troubleshooting

### Common Issues

1. **ImagePullBackOff**: Ensure the Docker image `bfljerum/google-search-mcp:latest` is accessible
2. **Environment Variables Not Set**: Verify your environment variables are exported correctly
3. **Invalid API Credentials**: Check your Google API key and CSE ID are valid
4. **Resource Constraints**: Adjust resource limits if pods are being killed

### Debug Commands

```bash
# Check deployment status
kubectl describe deployment -l app.kubernetes.io/name=google-search-mcp

# Check environment variables in pod
kubectl exec -it <pod-name> -- env | grep GOOGLE

# Check secrets (if using secret method)
kubectl get secrets -l app.kubernetes.io/name=google-search-mcp
```

## Uninstalling

```bash
# Using the uninstall script
cd helm
./uninstall.sh my-google-search

# Or using Helm directly
helm uninstall my-google-search
```

## Production Considerations

1. **Use environment variables** for MCP integration
2. **Set appropriate resource limits** based on usage
3. **Configure ingress** if external access is needed
4. **Enable HPA** for auto-scaling based on load
5. **Monitor logs** for API quota usage

## Example MCP Integration

When integrating with MCP clients, use the environment variable method:

```bash
# In your MCP client environment
export GOOGLE_API_KEY="AIzaSyCH6..."
export GOOGLE_CSE_ID="a60223a5..."

# Deploy the server
cd helm
./install.sh mcp-google-search --use-env-vars

# The server will be available at the service endpoint
kubectl get service -l app.kubernetes.io/name=google-search-mcp
```

This deployment guide ensures you can deploy the Google Search MCP Server in the way that best fits your infrastructure and integration requirements.
# Google Search MCP Helm Chart

A Helm chart for deploying the Google Search MCP Server to Kubernetes.

## Features

- **Multiple Server Types**: Deploy either the basic or enhanced Google Search MCP server
- **Multiple Transport Protocols**: Supports stdio, streamable-http, and sse transports
- **Interactive Installation Script**: Easy setup with prompts for API credentials
- **Namespace Support**: Deploy to any Kubernetes namespace
- **Dry-run Mode**: Template validation without actual installation
- **Uninstall Script**: Clean removal with optional namespace cleanup
- **HTTP Health Endpoints**: Built-in health checks for HTTP transports
- **Auto-Service Configuration**: Automatically enables Kubernetes service for HTTP transports

## Important Note

The Google Search MCP server supports multiple configurations:
- **Server Types**: 
  - `enhanced`: Comprehensive server with 9 advanced search tools (recommended)
  - `basic`: Simple server with basic Google search functionality
- **Transport Protocols**:
  - `stdio`: Traditional MCP communication via kubectl exec (default for compatibility)
  - `streamable-http`: HTTP-based transport for cloud deployments and LibreChat integration
  - `sse`: Server-sent events transport

This chart automatically configures the appropriate Kubernetes resources based on the selected server type and transport.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- A valid Google API key with Custom Search API enabled (can be configured after installation)
- A Google Custom Search Engine ID (can be configured after installation)

## Installation

### Quick Install

Run the interactive installation script:

```bash
./install.sh
```

The script will prompt you for:
- Kubernetes namespace (default: `mcp-servers`)
- Google API key (optional - can be configured later)
- Google Custom Search Engine ID (optional - can be configured later)

### Advanced Installation

#### Enhanced Server with SSE Transport (Recommended)

```bash
./install.sh google-search-mcp \
  --server-type=enhanced \
  --transport=sse \
  --image-tag=latest
```

#### Basic Server with stdio Transport

```bash
./install.sh google-search-mcp \
  --server-type=basic \
  --transport=stdio
```

#### HTTP Transport for LibreChat Integration

```bash
./install.sh google-search-mcp \
  --server-type=enhanced \
  --transport=streamable-http
```

#### Manual Helm Installation

```bash
# Create namespace
kubectl create namespace mcp-servers

# Install with Helm
helm install google-search-mcp ./helm \
  --namespace mcp-servers \
  --set secret.googleApiKey="your_google_api_key_here" \
  --set secret.googleCseId="your_custom_search_engine_id_here" \
  --set mcp.serverType="enhanced" \
  --set mcp.transport="sse"
```

### Environment Variables

Set these before running the install script to skip prompts:

```bash
export GOOGLE_API_KEY="your_google_api_key_here"
export GOOGLE_CSE_ID="your_custom_search_engine_id_here"
export NAMESPACE="mcp-servers"
./install.sh
```

### Using Environment Variables

You can configure the deployment to use environment variables instead of Kubernetes secrets:

```bash
# Set environment variables
export GOOGLE_API_KEY="your_api_key_here"
export GOOGLE_CSE_ID="your_cse_id_here"

# Install with environment variables
./install.sh mcp-google-search --use-env-vars
```

Or via Helm directly:
```bash
helm install google-search-mcp ./helm \
  --set secret.useEnvVars=true \
  --set secret.googleApiKey="your_api_key_here" \
  --set secret.googleCseId="your_cse_id_here"
```

### Configuring API Keys After Installation

If you didn't provide API keys during installation, you can configure them later:

#### Via kubectl:
```bash
# Update the secret directly
kubectl patch secret google-search-mcp-secret -n mcp-servers --patch='{"data":{"google-api-key":"'$(echo -n "YOUR_ACTUAL_API_KEY" | base64)'","google-cse-id":"'$(echo -n "YOUR_ACTUAL_CSE_ID" | base64)'"}}'

# Restart the deployment to pick up new credentials
kubectl rollout restart deployment google-search-mcp -n mcp-servers
```

#### Via Helm upgrade:
```bash
helm upgrade google-search-mcp ./helm -n mcp-servers \
  --set secret.googleApiKey="YOUR_ACTUAL_API_KEY" \
  --set secret.googleCseId="YOUR_ACTUAL_CSE_ID"
```

## Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `google-search-mcp` |
| `image.tag` | Container image tag | `latest` |
| `mcp.serverType` | Server type (enhanced/basic) | `enhanced` |
| `mcp.transport` | Transport protocol | `sse` |
| `mcp.server.host` | Server bind host | `0.0.0.0` |
| `mcp.server.port` | Server bind port | `8000` |
| `secret.googleApiKey` | Google API Key | `""` |
| `secret.googleCseId` | Google Custom Search Engine ID | `""` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `ingress.enabled` | Enable ingress | `false` |
| `autoscaling.enabled` | Enable HPA | `false` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |

## Usage

### Connecting from MCP Clients

#### For stdio transport (kubectl exec):

```bash
# Get the pod name
POD_NAME=$(kubectl get pods -l app.kubernetes.io/name=google-search-mcp -o jsonpath="{.items[0].metadata.name}")

# Execute the MCP server interactively
kubectl exec -it $POD_NAME -- python enhanced_google_search_server.py
```

#### For HTTP transports (sse/streamable-http):

```bash
# Port forward to access locally
kubectl port-forward service/google-search-mcp 8080:8000

# Test the server
curl http://localhost:8080
```

### LibreChat Integration

For LibreChat integration using HTTP transport, add to your `librechat.yaml`:

```yaml
mcpServers:
  google-search-mcp:
    type: "streamable-http"
    url: "http://google-search-mcp.mcp-servers.svc.cluster.local:8000"
    timeout: 30000
    serverInstructions: |
      This server provides comprehensive Google Search functionality.
      Available tools include web search, image search, date-range filtering,
      site-specific searches, file type searches, and more.
```

For external access (via port-forward):
```yaml
mcpServers:
  google-search-mcp:
    type: "streamable-http"  
    url: "http://localhost:8080"
    timeout: 30000
```

### Claude Desktop Integration

For Claude Desktop integration, use kubectl as a transport:

```json
{
  "mcpServers": {
    "google-search-mcp": {
      "command": "kubectl",
      "args": [
        "exec", "-i", "POD_NAME", "--namespace", "mcp-servers", "--",
        "python", "enhanced_google_search_server.py"
      ]
    }
  }
}
```

## Available Tools

### Enhanced Server Tools

The enhanced server provides 9 comprehensive search tools:

1. **search_google**: Advanced web search with pagination and localization
2. **search_images**: Image search with size/type filters
3. **search_by_date_range**: Date-filtered search
4. **search_site_specific**: Site-restricted search
5. **search_file_type**: File type search (PDF, DOC, etc.)
6. **search_related**: Find related pages
7. **search_cached**: Get cached page versions
8. **get_search_suggestions**: Get search suggestions
9. **get_api_status**: Check API configuration and quota

### Basic Server Tools

The basic server provides:

1. **search_google**: Basic Google search functionality

## Management Commands

### Check Deployment Status

```bash
kubectl get pods -l app.kubernetes.io/name=google-search-mcp
kubectl logs -l app.kubernetes.io/name=google-search-mcp -f
```

### Upgrade

```bash
./install.sh --upgrade --image-tag=v1.0.1
```

### Switch Server Type

```bash
./install.sh --upgrade --server-type=basic
```

### Change Transport

```bash
./install.sh --upgrade --transport=streamable-http
```

### Uninstall

```bash
./uninstall.sh
```

## Examples

### Development Values

Create `examples/values-dev.yaml`:

```yaml
replicaCount: 1
mcp:
  serverType: enhanced
  transport: sse
image:
  tag: latest
  pullPolicy: Always
resources:
  requests:
    cpu: 50m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
```

### Production Values

Create `examples/values-prod.yaml`:

```yaml
replicaCount: 3
mcp:
  serverType: enhanced
  transport: streamable-http
image:
  tag: v1.0.0
  pullPolicy: IfNotPresent
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: google-search-mcp.example.com
      paths:
        - path: /
          pathType: Prefix
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| 🔑 **API Key Issues** | Ensure your Google Cloud project has the Custom Search API enabled |
| 🚦 **Rate Limits** | Google Custom Search has daily query limits |
| 🔍 **Search Engine Configuration** | Make sure your CSE is configured to search the web |
| 📁 **Environment Variables** | Verify your API credentials are correctly configured |

### Debugging Commands

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=google-search-mcp

# View logs
kubectl logs -l app.kubernetes.io/name=google-search-mcp

# Check service
kubectl get svc google-search-mcp

# Check secrets
kubectl get secret google-search-mcp-secret -o yaml

# Debug pod
kubectl exec -it <pod-name> -- /bin/sh
```

## Security Considerations

- API keys are stored as Kubernetes secrets
- Pod runs as non-root user (UID 1001)
- Security contexts enforce non-privileged execution
- Read-only root filesystem (except for logs)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Test your changes with `helm lint` and `helm template`
4. Submit a pull request

## License

This project is open source. Please check the repository for license details.
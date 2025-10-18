# Placer.ai MCP Server Helm Chart

This Helm chart deploys the Placer.ai MCP (Model Context Protocol) server to Kubernetes, providing location analytics and foot traffic analysis capabilities.

## Features

- **Location Discovery**: Search for retail locations and points of interest
- **Foot Traffic Analysis**: Real-time and historical visit patterns
- **Demographics Insights**: Age, income, and interest analysis
- **Competitor Analysis**: Cross-brand performance comparison
- **Trade Area Analysis**: Geographic area insights
- **Multiple Transport Protocols**: Support for stdio, streamable-http, and SSE protocols
- **Kubernetes Native**: Full Kubernetes deployment with proper secret management
- **Interactive Installation Script**: Easy setup with prompts for API key
- **Safe Uninstall Script**: Clean removal with dry-run and safety checks
- **Auto-scaling**: HPA support for handling varying loads
- **Health Monitoring**: Built-in health checks and observability

## Important Note

The Placer.ai MCP server supports three transport protocols:
- **stdio**: Traditional MCP communication via kubectl exec (interactive mode)
- **streamable-http**: HTTP-based MCP communication (recommended)
- **sse**: Server-sent events transport for streaming integrations

This chart is configured to use streamable-http transport by default, which provides better performance and is suitable for HTTP-based MCP client integrations.

## Prerequisites

- Kubernetes 1.16+
- Helm 3.2.0+
- Valid Placer.ai API key (get from https://www.placer.ai/)

## Installation

### Quick Start with Installation Script

The easiest way to install the chart is using the interactive installation script:

```bash
./install.sh
```

The script will prompt you for:
- Kubernetes namespace (defaults to `mcp-servers`)
- Placer.ai API key

You can also set environment variables to skip prompts:
```bash
NAMESPACE=placer PLACER_AI_API_KEY=your_key ./install.sh my-release-name
```

### Manual Installation

```bash
# Add the repository (when published)
helm repo add bluefoxlabsai https://charts.bluefoxlabsai.com
helm repo update

# Install with required values
helm install placer-ai-mcp bluefoxlabsai/placer-ai-mcp \
  --namespace mcp-servers --create-namespace \
  --set placerAI.apiKey=your_placer_ai_api_key
```

### Local Installation

```bash
# Clone the repository
git clone https://github.com/bluefoxlabsai/placer-ai-mcp.git
cd placer-ai-mcp/helm

# Install from local chart
helm install placer-ai-mcp . \
  --namespace mcp-servers --create-namespace \
  --set placerAI.apiKey=your_placer_ai_api_key
```

## Configuration

### Required Values

| Parameter | Description | Required |
|-----------|-------------|----------|
| `placerAI.apiKey` | Your Placer.ai API key | ✅ |

### Optional Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `ghcr.io/bluefoxlabsai/placer-ai-mcp` |
| `image.tag` | Container image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `mcp.transport` | MCP transport protocol | `streamable-http` |
| `mcp.server.host` | Server bind host | `0.0.0.0` |
| `mcp.server.port` | Server port | `8000` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |

### Placer.ai Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `placerAI.baseUrl` | Placer.ai API base URL | `https://api.placer.ai/v1` |
| `placerAI.timeout` | Request timeout (seconds) | `30` |
| `placerAI.cache.ttl` | Cache TTL (seconds) | `300` |
| `placerAI.cache.maxSize` | Maximum cache entries | `1000` |
| `placerAI.existingSecret` | Use existing secret for API key | `""` |

### Transport Configuration Examples

#### Streamable HTTP (Recommended)
```yaml
mcp:
  transport: "streamable-http"
  server:
    host: "0.0.0.0"
    port: 8000

service:
  enabled: "auto"  # Automatically enabled for HTTP transports
  type: ClusterIP
  port: 8000
```

#### Server-Sent Events (SSE)
```yaml
mcp:
  transport: "sse"
  server:
    host: "0.0.0.0"
    port: 8000

service:
  enabled: true
  type: ClusterIP
  port: 8000
```

#### Stdio (Interactive)
```yaml
mcp:
  transport: "stdio"

service:
  enabled: false  # No service needed for stdio
```

## Usage Examples

### Basic Installation
```bash
./install.sh placer-ai-mcp --namespace mcp-servers
```

### Production Installation
```bash
helm install placer-ai-mcp . \
  --namespace production \
  --create-namespace \
  --set placerAI.apiKey=your_production_api_key \
  --set replicaCount=3 \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=1Gi \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10
```

### Development Installation
```bash
helm install placer-ai-mcp-dev . \
  --namespace development \
  --create-namespace \
  --set placerAI.apiKey=your_dev_api_key \
  --set image.tag=dev \
  --set image.pullPolicy=Always
```

### Using Existing Secret
```bash
# Create secret manually
kubectl create secret generic placer-ai-secret \
  --from-literal=api-key=your_placer_ai_api_key \
  --namespace mcp-servers

# Install using existing secret
helm install placer-ai-mcp . \
  --namespace mcp-servers \
  --set placerAI.existingSecret=placer-ai-secret
```

## Accessing the Server

### Port Forward for Local Access
```bash
kubectl port-forward service/placer-ai-mcp 8000:8000 -n mcp-servers
```

### Health Check
```bash
curl http://localhost:8000/health
```

### MCP Connection (Streamable HTTP)
```bash
# From within cluster
http://placer-ai-mcp.mcp-servers.svc.cluster.local:8000

# From localhost (with port-forward)
http://localhost:8000
```

### Interactive Mode (Stdio)
```bash
kubectl exec -it deployment/placer-ai-mcp -n mcp-servers -- uv run mcp-placer-ai
```

## Monitoring and Debugging

### Check Pod Status
```bash
kubectl get pods -l app.kubernetes.io/name=placer-ai-mcp -n mcp-servers
```

### View Logs
```bash
kubectl logs -f deployment/placer-ai-mcp -n mcp-servers
```

### Debug Pod Issues
```bash
kubectl describe pod -l app.kubernetes.io/name=placer-ai-mcp -n mcp-servers
```

### Test Server Connection
```bash
kubectl exec -it deployment/placer-ai-mcp -n mcp-servers -- curl http://localhost:8000/health
```

## Upgrading

### Using Install Script
```bash
./install.sh --upgrade
```

### Manual Upgrade
```bash
helm upgrade placer-ai-mcp . \
  --namespace mcp-servers \
  --set placerAI.apiKey=your_api_key
```

## Uninstalling

### Using Uninstall Script
```bash
./uninstall.sh
```

### Manual Uninstall
```bash
helm uninstall placer-ai-mcp --namespace mcp-servers
```

### Complete Cleanup (including namespace)
```bash
./uninstall.sh --purge-namespace
```

## Security Considerations

- **API Key Storage**: API keys are stored as Kubernetes secrets and base64 encoded
- **Network Policies**: Consider implementing network policies to restrict access
- **RBAC**: The chart creates a minimal service account with no additional permissions
- **Container Security**: Containers run as non-root user (UID 1000)
- **Resource Limits**: Resource limits are enforced to prevent resource exhaustion

## Troubleshooting

### Common Issues

1. **API Key Invalid**
   ```bash
   kubectl logs deployment/placer-ai-mcp -n mcp-servers
   # Look for: "401 Unauthorized" or "Invalid API key"
   ```

2. **Service Not Accessible**
   ```bash
   kubectl get service placer-ai-mcp -n mcp-servers
   kubectl describe service placer-ai-mcp -n mcp-servers
   ```

3. **Pod CrashLoopBackOff**
   ```bash
   kubectl describe pod -l app.kubernetes.io/name=placer-ai-mcp -n mcp-servers
   kubectl logs deployment/placer-ai-mcp -n mcp-servers --previous
   ```

### Debug Mode

Enable verbose logging:
```bash
helm upgrade placer-ai-mcp . \
  --set env[0].name=MCP_VERBOSE \
  --set env[0].value=true
```

## Support

- 📧 **Email**: support@bluefoxlabsai.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/bluefoxlabsai/placer-ai-mcp/issues)
- 📖 **Documentation**: [Official Docs](https://docs.bluefoxlabsai.com/mcp/placer-ai)

## Chart Information

- **Chart Version**: 0.1.0
- **App Version**: 0.1.0
- **Kubernetes Version**: 1.16+
- **Maintained by**: BlueFox Labs AI
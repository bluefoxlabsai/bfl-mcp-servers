# Nasdaq Data Link MCP Helm Chart

This Helm chart deploys the Nasdaq Data Link MCP (Model Context Protocol) server on a Kubernetes cluster.

## Features

- **Multiple Transport Protocols**: Supports stdio, streamable-http, and sse transports
- **Interactive Installation Script**: Easy setup with prompts for namespace and API key
- **Namespace Support**: Deploy to any Kubernetes namespace
- **Dry-run Mode**: Template validation without actual installation  
- **Uninstall Script**: Clean removal with optional namespace cleanup
- **HTTP Health Endpoints**: Built-in health checks for HTTP transports
- **Auto-Service Configuration**: Automatically enables Kubernetes service for HTTP transports

## Important Note

The Nasdaq Data Link MCP server supports multiple transport protocols:
- **stdio**: Traditional MCP communication via kubectl exec (default for compatibility)  
- **streamable-http**: HTTP-based transport for cloud deployments and LibreChat integration
- **sse**: Server-sent events transport

This chart automatically configures the appropriate Kubernetes resources based on the selected transport.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- A valid Nasdaq Data Link API key

## Installation

### Quick Start with Installation Script

The easiest way to install the chart is using the interactive installation script:

```bash
./install.sh
```

The script will prompt you for:
- Kubernetes namespace (defaults to `default`)
- Nasdaq Data Link API key

You can also set environment variables to skip the prompts:
```bash
NAMESPACE=nasdaq NASDAQ_API_KEY=your_api_key ./install.sh my-release-name
```

### Manual Installation

1. Create namespace (optional):
```bash
kubectl create namespace nasdaq
```

2. Install the chart with namespace:
```bash
helm install my-nasdaq-mcp ./helm-chart \
  --namespace nasdaq \
  --set secret.nasdaqApiKey="YOUR_NASDAQ_API_KEY"
```

3. Get pod name and connect to MCP server:
```bash
export POD_NAME=$(kubectl get pods --namespace nasdaq -l "app.kubernetes.io/name=nasdaq-data-link-mcp" -o jsonpath="{.items[0].metadata.name}")
kubectl exec -it $POD_NAME --namespace nasdaq -- python nasdaq_data_link_mcp_os/server.py
```

### HTTP Transport Installation

For LibreChat integration or HTTP-based access:

```bash
# Install with HTTP transport
helm install my-nasdaq-mcp ./helm-chart \
  --namespace nasdaq \
  --set secret.nasdaqApiKey="YOUR_NASDAQ_API_KEY" \
  --set mcp.transport="streamable-http"
```

Then access via port-forward:
```bash
kubectl port-forward service/my-nasdaq-mcp-nasdaq-data-link-mcp 8080:8080 --namespace nasdaq
curl http://localhost:8080/health
```

### LibreChat Integration

For LibreChat integration using HTTP transport, add to your `librechat.yaml`:

```yaml
mcpServers:
  nasdaq-data-link-mcp:
    type: "streamable-http"
    url: "http://my-nasdaq-mcp-nasdaq-data-link-mcp.nasdaq.svc.cluster.local:8080"
    timeout: 30000
    serverInstructions: |
      This server provides access to Nasdaq Data Link financial and economic data.
      Available tools include company fundamentals, retail trading activity, 
      trade summary data, World Bank indicators, and mutual fund data.
```

For external access (via port-forward):
```yaml
mcpServers:
  nasdaq-data-link-mcp:
    type: "streamable-http"  
    url: "http://localhost:8080"
    timeout: 30000
```

### Installation with Custom Values

1. Create a `my-values.yaml` file:
```yaml
secret:
  nasdaqApiKey: "YOUR_NASDAQ_API_KEY"

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi

ingress:
  enabled: true
  hosts:
    - host: nasdaq-mcp.example.com
      paths:
        - path: /
          pathType: Prefix
```

2. Install with custom values:
```bash
helm install my-nasdaq-mcp ./helm-chart -f my-values.yaml
```

## Configuration

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `stefanoamorelli/nasdaq-data-link-mcp` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8080` |
| `secret.create` | Create secret for API key | `true` |
| `secret.nasdaqApiKey` | Nasdaq Data Link API key | `""` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `ingress.enabled` | Enable ingress | `false` |

## Usage

### Connecting from MCP Clients

The MCP server runs in a containerized environment with the API key pre-configured. To use it:

1. **Direct execution in the pod**:
```bash
# Get the pod name
POD_NAME=$(kubectl get pods -l app.kubernetes.io/name=nasdaq-data-link-mcp -o jsonpath="{.items[0].metadata.name}")

# Execute the MCP server interactively
kubectl exec -it $POD_NAME -- python nasdaq_data_link_mcp_os/server.py
```

2. **For MCP client integration**, you can use kubectl as a transport:
```json
{
  "mcpServers": {
    "nasdaq-data-link-mcp": {
      "command": "kubectl",
      "args": [
        "exec", "-i", "POD_NAME", "--",
        "python", "nasdaq_data_link_mcp_os/server.py"
      ]
    }
  }
}
```

Replace `POD_NAME` with the actual pod name from step 1.

### Available Data Sources

The MCP server provides access to these Nasdaq Data Link databases:
- **Equities 360 (E360)**: Company statistics and fundamental data
- **Nasdaq RTAT**: Retail trading activity tracker  
- **Trade Summary (TRDSUM)**: Consolidated trade data including OHLCV
- **World Bank (WB)**: World bank database
- **Nasdaq Fund Network (NFN)**: Mutual fund and investment product data

## Upgrading

```bash
helm upgrade my-nasdaq-mcp ./helm-chart
```

## Uninstalling

### Using the Uninstall Script

```bash
./uninstall.sh [release-name] [namespace]
```

Examples:
```bash
./uninstall.sh                           # Uninstall default release from default namespace
./uninstall.sh my-nasdaq-mcp             # Uninstall custom release from default namespace  
./uninstall.sh nasdaq-mcp nasdaq         # Uninstall from specific namespace
```

### Manual Uninstall

```bash
helm uninstall my-nasdaq-mcp --namespace nasdaq
```

## Troubleshooting

1. **Check pod status**:
```bash
kubectl get pods -l app.kubernetes.io/name=nasdaq-data-link-mcp
```

2. **View logs**:
```bash
kubectl logs -l app.kubernetes.io/name=nasdaq-data-link-mcp
```

3. **Check if API key is set**:
```bash
kubectl get secret my-nasdaq-mcp-nasdaq-data-link-mcp-secret -o yaml
```

## Security

- The chart runs with a non-root user and read-only root filesystem
- API keys are stored in Kubernetes Secrets
- Network policies can be enabled for additional security

## Contributing

Visit the main repository: https://github.com/stefanoamorelli/nasdaq-data-link-mcp
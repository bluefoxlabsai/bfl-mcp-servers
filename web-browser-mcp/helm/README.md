# Web Browser MCP Server Helm Chart

This Helm chart deploys the Web Browser MCP (Model Context Protocol) server to Kubernetes, providing web browsing and content extraction capabilities.

## Features

- **Web Content Extraction**: Browse websites and extract text content
- **Page Title Retrieval**: Get titles from web pages
- **Headless Browser**: Uses Chromium for reliable web scraping
- **Streamable HTTP Transport**: MCP streamable HTTP support on port 8000
- **Kubernetes Native**: Full Kubernetes deployment
- **Auto-scaling**: HPA support for handling varying loads
- **Health Monitoring**: Built-in health checks

## Prerequisites

- Kubernetes 1.16+
- Helm 3.2.0+

## Installation

### Quick Start with Installation Script

```bash
./install.sh
```

The script will prompt you for:
- Kubernetes namespace (defaults to `default`)
- Release name (defaults to `web-browser-mcp`)

### Manual Installation

```bash
# Add the chart to your local repository
helm install web-browser-mcp ./helm

# Or specify a namespace
helm install web-browser-mcp ./helm -n mcp-namespace
```

### Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Docker image repository | `mcp-web-browser` |
| `image.tag` | Docker image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `1Gi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `256Mi` |

## Usage

After installation, the MCP server will be available at:
- HTTP endpoint: `http://<service-name>.<namespace>.svc.cluster.local:8000`
- Streamable HTTP path: `/mcp`

## Uninstall

```bash
./uninstall.sh
```

Or manually:
```bash
helm uninstall web-browser-mcp
```

## Troubleshooting

### Check pod status
```bash
kubectl get pods -l app.kubernetes.io/name=web-browser-mcp
```

### View logs
```bash
kubectl logs -l app.kubernetes.io/name=web-browser-mcp
```

### Health check
```bash
curl http://<service-name>.<namespace>.svc.cluster.local:8000/health
```
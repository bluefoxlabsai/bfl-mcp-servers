# SharePoint MCP Helm Chart

This Helm chart deploys the SharePoint MCP (Model Context Protocol) server on Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- SharePoint Online or SharePoint Server access
- Azure AD App Registration (for SharePoint Online)

## Installation

### Quick Start

```bash
# Interactive installation
./install.sh

# Or with environment variables
NAMESPACE=mcp-servers \
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite \
AZURE_CLIENT_ID=your_client_id \
AZURE_CLIENT_SECRET=your_client_secret \
AZURE_TENANT_ID=your_tenant_id \
./install.sh sharepoint-mcp
```

### Manual Installation

```bash
helm install sharepoint-mcp . \
  --namespace mcp-servers --create-namespace \
  --set secret.sharepointSiteUrl=https://yourtenant.sharepoint.com/sites/yoursite \
  --set secret.azureClientId=your_client_id \
  --set secret.azureClientSecret=your_client_secret \
  --set secret.azureTenantId=your_tenant_id
```

## Configuration

### Required Values

| Parameter | Description | Example |
|-----------|-------------|---------|
| `secret.sharepointSiteUrl` | SharePoint site URL | `https://yourtenant.sharepoint.com/sites/yoursite` |
| `secret.azureClientId` | Azure AD client ID | `12345678-1234-1234-1234-123456789012` |
| `secret.azureClientSecret` | Azure AD client secret | `your-client-secret` |
| `secret.azureTenantId` | Azure AD tenant ID | `87654321-4321-4321-4321-210987654321` |

### Optional Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mcp.transport` | Transport protocol (stdio, sse, streamable-http) | `sse` |
| `secret.readOnlyMode` | Enable read-only mode | `false` |
| `secret.verboseLogging` | Enable verbose logging | `false` |
| `image.tag` | Docker image tag | `latest` |
| `replicaCount` | Number of replicas | `1` |

## Usage

### Accessing the Service

After installation, you can access the MCP server:

```bash
# Port forward to localhost
kubectl --namespace mcp-servers port-forward service/sharepoint-mcp 8080:8000

# Test the service
curl http://localhost:8080/sse
```

### MCP Client Configuration

For Claude Desktop or other MCP clients:

```json
{
  "mcpServers": {
    "sharepoint-mcp": {
      "type": "sse",
      "url": "http://localhost:8080/sse"
    }
  }
}
```

## Uninstallation

```bash
# Interactive uninstallation
./uninstall.sh

# Or manual
helm uninstall sharepoint-mcp --namespace mcp-servers
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods --namespace mcp-servers -l app.kubernetes.io/name=sharepoint-mcp
```

### View Logs

```bash
kubectl logs --namespace mcp-servers -l app.kubernetes.io/name=sharepoint-mcp -f
```

### Common Issues

1. **Authentication Errors**: Verify Azure AD app permissions and credentials
2. **Connection Issues**: Check SharePoint site URL and network connectivity
3. **Pod Startup Issues**: Review resource limits and image pull policies

## Values Reference

See [values.yaml](values.yaml) for the complete list of configurable values.
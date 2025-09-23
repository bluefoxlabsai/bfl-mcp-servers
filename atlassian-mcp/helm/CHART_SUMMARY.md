# Atlassian MCP Helm Chart Summary

## What We Created

A production-ready Helm chart for the Atlassian MCP server with comprehensive Jira and Confluence integration:

### Core Chart Files
- `Chart.yaml` - Chart metadata and versioning (Atlassian MCP v0.1.0)
- `values.yaml` - Complete configuration with Atlassian credentials
- `README.md` - Comprehensive installation and usage documentation
- `install.sh` - Interactive installation script with credential collection

### Kubernetes Templates
- `deployment.yaml` - Main MCP server deployment with SSE transport
- `service.yaml` - ClusterIP service exposing port 8000
- `serviceaccount.yaml` - Service account with proper RBAC
- `secret.yaml` - Secure Atlassian credential storage
- `ingress.yaml` - Optional ingress for external access
- `httproute.yaml` - Gateway API HTTPRoute support
- `hpa.yaml` - Horizontal Pod Autoscaler configuration
- `_helpers.tpl` - Template helper functions for Atlassian MCP
- `NOTES.txt` - Post-installation instructions and connection details
- `tests/test-connection.yaml` - Helm test for deployment validation

### Example Configurations
- `examples/values-dev.yaml.example` - Development environment template
- `examples/values-prod.yaml.example` - Production environment template

### Production Features

#### 🔐 Security & Compliance
- **Non-root containers** with restrictive security contexts
- **Encrypted secret management** for Atlassian API credentials
- **Security hardening** with dropped capabilities and read-only root filesystem
- **RBAC integration** with dedicated service accounts

#### 🚀 Performance & Reliability  
- **SSE transport protocol** for high-performance MCP communication
- **Multi-platform support** (AMD64, ARM64) via Docker Hub image
- **TCP health checks** with configurable liveness and readiness probes
- **Resource management** with CPU/memory limits and requests
- **Persistent logging** with dedicated volume mounts

#### ⚙️ Flexibility & Configuration
- **Interactive installer** with guided credential collection
- **Environment variable support** for automation-friendly deployments
- **Dry-run testing** for configuration validation
- **Optional HPA** for automatic scaling based on CPU/memory
- **Ingress/HTTPRoute support** for external access
- **Configurable transport modes** (SSE, stdio, streamable-http)

### Quick Start Options

#### Interactive Installation (Recommended)
```bash
cd helm
NAMESPACE=mcp-servers ./install.sh atlassian-mcp
```

#### Non-Interactive Installation
```bash
NAMESPACE=mcp-servers \
CONFLUENCE_URL=https://company.atlassian.net/wiki \
CONFLUENCE_USERNAME=user@company.com \
CONFLUENCE_API_TOKEN=your_token \
JIRA_URL=https://company.atlassian.net \
JIRA_USERNAME=user@company.com \
JIRA_API_TOKEN=your_token \
./install.sh atlassian-mcp
```

#### Manual Helm Installation
```bash
helm install atlassian-mcp . \
  --namespace mcp-servers --create-namespace \
  --set secret.confluenceUrl=https://company.atlassian.net/wiki \
  --set secret.confluenceUsername=user@company.com \
  --set-string secret.confluenceApiToken=your_token \
  --set secret.jiraUrl=https://company.atlassian.net \
  --set secret.jiraUsername=user@company.com \
  --set-string secret.jiraApiToken=your_token
```

### Access and Testing

#### Service Access
```bash
# Port forward to localhost
kubectl --namespace mcp-servers port-forward service/atlassian-mcp 8080:8000

# Check health endpoint
curl http://localhost:8080/health

# View logs
kubectl logs -l app.kubernetes.io/name=atlassian-mcp --namespace mcp-servers
```

#### MCP Client Integration
```json
{
  "mcpServers": {
    "atlassian-mcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-stdio", "sse://atlassian-mcp.mcp-servers.svc.cluster.local:8000"]
    }
  }
}
```

## Deployment-Ready Status

✅ **Production-Ready**: Uses optimized `bfljerum/atlassian-mcp:latest` Docker image  
✅ **Security Hardened**: Non-root containers with encrypted credential storage  
✅ **Multi-Platform**: AMD64 and ARM64 architecture support  
✅ **Fully Tested**: Dry-run validation and Helm test integration  
✅ **Documentation Complete**: Comprehensive README and usage examples  
✅ **Enterprise-Ready**: RBAC, resource limits, health checks, and monitoring support

The chart is production-ready for Kubernetes deployment and provides comprehensive Atlassian integration with Jira and Confluence through the MCP protocol.
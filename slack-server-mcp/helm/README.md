# Slack MCP Server Helm Chart

This Helm chart deploys the Slack MCP (Model Context Protocol) server on a Kubernetes cluster, providing seamless integration between AI assistants and Slack workspaces.

## 🚀 Features

- **Multiple Transport Protocols**: Supports stdio, SSE, and HTTP transports
- **Interactive Installation Script**: Easy setup with prompts for namespace and Slack tokens
- **Namespace Support**: Deploy to any Kubernetes namespace
- **Dry-run Mode**: Template validation without actual installation  
- **Uninstall Script**: Clean removal with optional namespace cleanup
- **HTTP Health Endpoints**: Built-in health checks for HTTP transport
- **Auto-Service Configuration**: Automatically enables Kubernetes service for HTTP transport
- **Security**: Supports existing secrets or creates new ones for Slack tokens
- **Production Ready**: Includes resource limits, security contexts, and autoscaling

## 📋 Important Note

The Slack MCP server supports three transport protocols:
- **stdio**: Traditional MCP communication via kubectl exec (for AI assistants)  
- **sse**: Server-Sent Events transport for real-time web applications (recommended for Kubernetes)
- **http**: HTTP-based transport for web applications and remote access

This chart automatically configures the appropriate Kubernetes resources based on the selected transport.

## 🔧 Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Valid Slack Bot User OAuth Token (`xoxb-...`)
- Valid Slack User OAuth Token (`xoxp-...`) for search features

## 🚀 Installation

### Quick Start with Installation Script

The easiest way to install the chart is using the interactive installation script:

```bash
./install.sh
```

The script will prompt you for:
- Kubernetes namespace (defaults to `mcp-servers`)
- Slack Bot Token (`xoxb-...`)
- Slack User Token (`xoxp-...`)

You can also set environment variables to skip the prompts:
```bash
NAMESPACE=slack SLACK_BOT_TOKEN=xoxb-xxx SLACK_USER_TOKEN=xoxp-xxx ./install.sh my-release-name
```

### Advanced Installation Options

```bash
# Install with SSE transport (recommended for Kubernetes)
./install.sh --transport=sse

# Install with HTTP transport
./install.sh --transport=http

# Install with specific image tag
./install.sh --image-tag=v0.1.4

# Install with custom values file
./install.sh -f examples/values-prod.yaml

# Upgrade existing installation
./install.sh --upgrade

# Dry-run to validate configuration
./install.sh --dry-run
```

### Manual Installation with Helm

If you prefer to use Helm directly:

```bash
# Create namespace
kubectl create namespace mcp-servers

# Install the chart
helm install slack-mcp-server . \
  --namespace mcp-servers \
  --set slack.botToken=xoxb-your-bot-token \
  --set slack.userToken=xoxp-your-user-token
```

## 🔧 Configuration

### Transport Modes

#### STDIO Mode (Default)
Best for AI assistant integration:
```yaml
mcp:
  transport: "stdio"

# Service is automatically disabled for stdio
service:
  enabled: auto  # Will be false for stdio
```

#### SSE Mode (Recommended for Kubernetes)
Best for real-time web applications with Server-Sent Events:
```yaml
mcp:
  transport: "sse"
  server:
    host: "0.0.0.0"
    port: 8000

# Service is automatically enabled for SSE
service:
  enabled: auto  # Will be true for sse
  type: ClusterIP
  port: 8000
```

#### HTTP Mode  
Best for traditional web applications and remote access:
```yaml
mcp:
  transport: "http"
  server:
    host: "0.0.0.0"
    port: 8000

# Service is automatically enabled for HTTP
service:
  enabled: auto  # Will be true for http
  type: ClusterIP
  port: 8000
```

### Slack Token Configuration

#### Option 1: Direct Values (Development)
```yaml
slack:
  botToken: "xoxb-your-bot-token"
  userToken: "xoxp-your-user-token"
  safeSearch: false
```

#### Option 2: Existing Secret (Production)
```yaml
slack:
  existingSecret: "slack-credentials"
  secretKeys:
    botToken: "bot-token"
    userToken: "user-token"
```

Create the secret:
```bash
kubectl create secret generic slack-credentials \
  --from-literal=bot-token=xoxb-your-bot-token \
  --from-literal=user-token=xoxp-your-user-token \
  -n mcp-servers
```

### Resource Configuration

```yaml
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

# Enable autoscaling
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

## 📊 Example Values Files

The `examples/` directory contains pre-configured values files:

### Development Environment
```bash
./install.sh -f examples/values-dev.yaml.example
```

Features:
- SSE transport for better Kubernetes compatibility
- Ingress enabled
- Lower resource limits
- Safe search enabled

### Production Environment
```bash
./install.sh -f examples/values-prod.yaml.example
```

Features:
- STDIO transport (MCP standard)
- Multiple replicas for HA
- Production security contexts
- Autoscaling enabled
- External secret management
- Node selectors and affinity rules

## 🎯 Usage

### STDIO Mode (AI Assistants)

After installation, connect to the server:

```bash
# Get pod name
export POD_NAME=$(kubectl get pods -n mcp-servers -l "app.kubernetes.io/name=slack-mcp-server" -o jsonpath="{.items[0].metadata.name}")

# Connect via kubectl exec
kubectl exec -it -n mcp-servers $POD_NAME -- uv run slack-mcp-server
```

### SSE Mode (Web Applications)

Access the SSE endpoint:

```bash
# Port forward to access locally
kubectl port-forward -n mcp-servers service/slack-mcp-server 8000:8000

# Test the health endpoint
curl http://localhost:8000/health

# SSE endpoint available at
curl http://localhost:8000/sse
```

### HTTP Mode (Web Applications)

Access the HTTP endpoint:

```bash
# Port forward to access locally
kubectl port-forward -n mcp-servers service/slack-mcp-server 8000:8000

# Test the health endpoint
curl http://localhost:8000/health
```

## 🧪 Available Tools

The Slack MCP Server provides these tools:

| Tool | Description |
|------|-------------|
| `slack_list_channels` | List public channels with pagination |
| `slack_post_message` | Post messages to channels |
| `slack_reply_to_thread` | Reply to message threads |
| `slack_add_reaction` | Add emoji reactions |
| `slack_get_channel_history` | Get channel message history |
| `slack_get_thread_replies` | Get thread replies |
| `slack_get_users` | Get workspace users |
| `slack_get_user_profiles` | Get user profile information |
| `slack_search_messages` | Search messages with filters |
| `slack_search_channels` | Search for channels |
| `slack_search_users` | Search for users |

## 🗑️ Uninstallation

### Using Uninstall Script

```bash
# Basic uninstallation
./uninstall.sh

# Uninstall specific release
./uninstall.sh my-slack-server

# Dry-run to see what would be deleted
./uninstall.sh --dry-run

# Keep namespace after uninstall
./uninstall.sh --keep-namespace
```

### Manual Uninstallation

```bash
# Uninstall with Helm
helm uninstall slack-mcp-server -n mcp-servers

# Optionally delete namespace
kubectl delete namespace mcp-servers
```

## 🔒 Security Considerations

### Production Deployment

1. **Use existing secrets** instead of values for tokens
2. **Enable resource limits** to prevent resource exhaustion
3. **Use specific image tags** instead of `latest`
4. **Configure security contexts** with non-root users
5. **Enable safe search mode** to restrict access to private content

### Network Security

```yaml
# Restrict ingress access
ingress:
  enabled: true
  annotations:
    nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/8,192.168.0.0/16"

# Use NetworkPolicies to restrict pod communication
# (NetworkPolicy manifests not included in this chart)
```

## 🔍 Troubleshooting

### Common Issues

#### Pod Not Starting
```bash
# Check pod status
kubectl get pods -n mcp-servers

# Check pod logs
kubectl logs -n mcp-servers deployment/slack-mcp-server

# Describe pod for events
kubectl describe pod -n mcp-servers <pod-name>
```

#### Invalid Slack Tokens
- Ensure tokens start with `xoxb-` (bot) and `xoxp-` (user)
- Verify tokens have required scopes in Slack App settings
- Check token expiration in Slack App dashboard

#### Service Not Accessible
- Verify transport mode matches service configuration
- Check if service is enabled for HTTP transport
- Ensure correct port forwarding or ingress configuration

### Debug Mode

Enable debug logging:
```bash
helm install slack-mcp-server . \
  --set env[0].name=LOG_LEVEL \
  --set env[0].value=DEBUG
```

## 📚 Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mcp.transport` | Transport protocol (stdio/sse/http) | `sse` |
| `mcp.server.host` | HTTP server bind host | `0.0.0.0` |
| `mcp.server.port` | HTTP server port | `8000` |
| `image.repository` | Container image repository | `bfljerum/slack-mcp-server` |
| `image.tag` | Container image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `slack.botToken` | Slack Bot User OAuth Token | `""` |
| `slack.userToken` | Slack User OAuth Token | `""` |
| `slack.safeSearch` | Enable safe search mode | `false` |
| `slack.existingSecret` | Name of existing secret | `""` |
| `service.enabled` | Enable service (auto/true/false) | `auto` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `ingress.enabled` | Enable ingress | `false` |
| `autoscaling.enabled` | Enable HPA | `false` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test with `helm template` and `helm lint`
5. Commit your changes (`git commit -am 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This chart is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🔗 Links

- **Source Code**: https://github.com/bluefoxlabsai/bfl-mcp-servers/tree/main/slack-server-mcp
- **Container Image**: https://hub.docker.com/r/bfljerum/slack-mcp-server
- **Issues**: https://github.com/bluefoxlabsai/bfl-mcp-servers/issues
- **Slack API Documentation**: https://api.slack.com/
- **MCP Specification**: https://modelcontextprotocol.io/

---

<div align="center">

**Made with ❤️ by [Blue Fox Labs AI](https://bluefoxlabs.ai)**

*Empowering AI with seamless integrations*

</div>
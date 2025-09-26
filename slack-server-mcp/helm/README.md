# Slack MCP Server Helm Chart

This Helm chart deploys the Slack MCP Server to a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Slack Bot Token and User Token

## Installing the Chart

### Quick Start

```bash
# Add the repository (if applicable)
# helm repo add bfl-mcp https://bluefoxlabsai.github.io/bfl-mcp-servers
# helm repo update

# Install with your Slack tokens
helm install slack-mcp . \
  --create-namespace \
  --namespace slack-server-mcp \
  --set slack.botToken=xoxb-your-bot-token \
  --set slack.userToken=xoxp-your-user-token
```

### Using External Secrets

For better security, create a Kubernetes secret first:

```bash
# Create the secret
kubectl create secret generic slack-credentials \
  --from-literal=bot-token=xoxb-your-bot-token \
  --from-literal=user-token=xoxp-your-user-token \
  -n slack-server-mcp

# Install using the external secret
helm install slack-mcp . \
  --namespace slack-server-mcp \
  --set slack.existingSecret=slack-credentials
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `ghcr.io/bluefoxlabsai/bfl-mcp-servers/slack-server-mcp` |
| `image.tag` | Container image tag | `latest` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `slack.botToken` | Slack Bot Token | `""` |
| `slack.userToken` | Slack User Token | `""` |
| `slack.safeSearch` | Enable safe search mode | `false` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |

## Slack Token Configuration

### Required Tokens

1. **Bot Token** (`xoxb-...`): For basic Slack operations
   - Required scopes: `channels:read`, `chat:write`, `users:read`, etc.

2. **User Token** (`xoxp-...`): For advanced search features
   - Required scopes: `search:read`

### Getting Tokens

1. Create a Slack App at https://api.slack.com/apps
2. Configure OAuth scopes in "OAuth & Permissions"
3. Install the app to your workspace
4. Copy the tokens from "OAuth & Permissions"

## Examples

### Basic Installation

```bash
helm install slack-mcp . \
  --namespace slack-server-mcp \
  --set slack.botToken=xoxb-your-bot-token \
  --set slack.userToken=xoxp-your-user-token
```

### With Resource Limits

```bash
helm install slack-mcp . \
  --namespace slack-server-mcp \
  --set slack.botToken=xoxb-your-bot-token \
  --set slack.userToken=xoxp-your-user-token \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=1Gi
```

### Using External Secret

```bash
# Create secret first
kubectl create secret generic slack-secret \
  --from-literal=bot-token=xoxb-your-bot-token \
  --from-literal=user-token=xoxp-your-user-token \
  -n slack-server-mcp

# Install chart
helm install slack-mcp . \
  --namespace slack-server-mcp \
  --set slack.existingSecret=slack-secret
```

## Verification

After installation, verify the deployment:

```bash
# Check pod status
kubectl get pods -n slack-server-mcp

# Check service
kubectl get svc -n slack-server-mcp

# Check logs
kubectl logs -n slack-server-mcp deployment/slack-mcp

# Port forward for testing
kubectl port-forward -n slack-server-mcp svc/slack-mcp 8000:8000
```

## Upgrading

```bash
helm upgrade slack-mcp . \
  --namespace slack-server-mcp \
  --set image.tag=v1.0.1
```

## Uninstalling

```bash
helm uninstall slack-mcp -n slack-server-mcp

# Clean up (optional)
kubectl delete namespace slack-server-mcp
```

## Troubleshooting

### Common Issues

1. **Invalid Auth Error**
   - Verify tokens are correct and not expired
   - Ensure tokens have required scopes

2. **Permission Denied**
   - Check if bot is added to private channels
   - Verify OAuth scopes are properly configured

3. **Service Not Accessible**
   - Check if service is running: `kubectl get pods -n slack-server-mcp`
   - Verify port forwarding or ingress configuration

### Debug Mode

Enable debug logging by setting environment variable:

```bash
kubectl set env deployment/slack-mcp SLACK_SDK_DEBUG=true -n slack-server-mcp
```

## Security Considerations

- Store tokens securely using Kubernetes secrets
- Use RBAC to limit access to secrets
- Regularly rotate API tokens
- Monitor API usage and errors
- Consider using external secret management (Vault, AWS Secrets Manager, etc.)

## Values Reference

See [values.yaml](./values.yaml) for all available configuration options.
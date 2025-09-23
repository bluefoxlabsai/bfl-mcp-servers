# Helm Values Examples

This directory contains example configuration files for different deployment environments of the Atlassian MCP server.

## Available Examples

### `values-dev.yaml.example`
Development environment configuration with:
- **Lower resource limits** (500m CPU, 512Mi memory)
- **Single replica** for simplicity
- **Verbose logging enabled** for debugging
- **Always pull policy** to get latest changes
- **No ingress** (use port-forward)
- **Relaxed security** for easier development

### `values-prod.yaml.example`
Production environment configuration with:
- **Higher resource limits** (1000m CPU, 1Gi memory)
- **Multiple replicas** (3) for high availability
- **Specific image tags** (never `latest`)
- **Ingress with TLS** for external access
- **HPA enabled** for auto-scaling (3-10 replicas)
- **Pod anti-affinity** to spread across nodes
- **Hardened security** contexts
- **External secret management** (manual secret creation)

## Usage

1. **Copy the appropriate example** to create your values file:
   ```bash
   # For development
   cp values-dev.yaml.example values-dev.yaml
   
   # For production  
   cp values-prod.yaml.example values-prod.yaml
   ```

2. **Edit the values file** to match your environment:
   - Replace `your-company.atlassian.net` with your actual Atlassian URL
   - Replace `your.email@company.com` with your service account email
   - Replace `yourdomain.com` with your actual domain
   - Update API tokens and credentials

3. **Install with your custom values**:
   ```bash
   # Development
   helm install atlassian-mcp . -f examples/values-dev.yaml --namespace dev
   
   # Production
   helm install atlassian-mcp . -f examples/values-prod.yaml --namespace prod
   ```

## Security Best Practices

- ✅ **Never commit real credentials** to version control
- ✅ **Use Kubernetes secrets** for sensitive data in production
- ✅ **Use specific image tags** in production (not `latest`)
- ✅ **Enable TLS** for production ingress
- ✅ **Review resource limits** based on your workload
- ✅ **Configure proper RBAC** if needed
- ✅ **Enable monitoring** and logging for production deployments

## Production Secret Management

For production deployments, create secrets manually instead of using Helm values:

```bash
kubectl create secret generic atlassian-mcp-credentials \
  --from-literal=confluence-url="https://your-company.atlassian.net/wiki" \
  --from-literal=confluence-username="service-account@your-company.com" \
  --from-literal=confluence-api-token="your_confluence_token" \
  --from-literal=jira-url="https://your-company.atlassian.net" \
  --from-literal=jira-username="service-account@your-company.com" \
  --from-literal=jira-api-token="your_jira_token" \
  --namespace your-production-namespace
```

Then set `secret.create: false` and `secret.name: "atlassian-mcp-credentials"` in your production values file.
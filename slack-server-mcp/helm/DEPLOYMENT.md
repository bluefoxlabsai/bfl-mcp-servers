# Slack MCP Server - Kubernetes Deployment Guide

This guide provides step-by-step instructions for deploying the Slack MCP Server with SSE transport on Kubernetes.

## 🚀 Quick Start

### 1. Prerequisites

- Kubernetes cluster (1.19+)
- Helm 3.0+
- kubectl configured
- Slack Bot Token (`xoxb-...`)
- Slack User Token (`xoxp-...`)

### 2. Deploy with SSE Transport (Recommended)

```bash
# Clone the repository
git clone https://github.com/bluefoxlabsai/bfl-mcp-servers.git
cd bfl-mcp-servers/slack-server-mcp/helm

# Run the interactive installer
./install.sh --transport=sse

# Or deploy directly with Helm
helm install slack-mcp . \
  --namespace mcp-servers \
  --create-namespace \
  --set mcp.transport=sse \
  --set slack.botToken=xoxb-your-bot-token \
  --set slack.userToken=xoxp-your-user-token
```

### 3. Verify Deployment

```bash
# Check pod status
kubectl get pods -n mcp-servers

# Check service
kubectl get service -n mcp-servers

# Test health endpoint
kubectl port-forward -n mcp-servers service/slack-mcp 8000:8000 &
curl http://localhost:8000/health
```

## 🔧 Configuration Options

### SSE Transport (Default)

```yaml
# values.yaml
mcp:
  transport: "sse"
  server:
    host: "0.0.0.0"
    port: 8000

service:
  enabled: "auto"  # Automatically enabled for SSE
  type: ClusterIP
  port: 8000

# Health checks enabled
livenessProbe:
  enabled: true
readinessProbe:
  enabled: true
```

### Production Configuration

```yaml
# Production values
replicaCount: 3

image:
  repository: bfljerum/slack-server-mcp
  tag: "0.1.5"  # Use specific version
  pullPolicy: Always

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

# Use existing secret for tokens
slack:
  existingSecret: "slack-credentials"
  secretKeys:
    botToken: "bot-token"
    userToken: "user-token"
  safeSearch: true
```

## 🌐 Accessing the Service

### Port Forward (Development)

```bash
kubectl port-forward -n mcp-servers service/slack-mcp-server 8000:8000

# Endpoints available:
# http://localhost:8000/health - Health check
# http://localhost:8000/sse - SSE MCP endpoint
```

### Ingress (Production)

```yaml
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: slack-mcp.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: slack-mcp-tls
      hosts:
        - slack-mcp.yourdomain.com
```

### Load Balancer

```yaml
service:
  type: LoadBalancer
  port: 8000
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
```

## 🔒 Security Best Practices

### 1. Use Secrets for Tokens

```bash
# Create secret
kubectl create secret generic slack-credentials \
  --from-literal=bot-token=xoxb-your-bot-token \
  --from-literal=user-token=xoxp-your-user-token \
  -n mcp-servers

# Reference in values
slack:
  existingSecret: "slack-credentials"
```

### 2. Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: slack-mcp-server
  namespace: mcp-servers
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: slack-server-mcp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS to Slack API
```

### 3. Pod Security Standards

```yaml
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: false
  runAsNonRoot: true
  runAsUser: 1000
```

## 📊 Monitoring

### Health Checks

The SSE transport includes built-in health endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "service": "Slack MCP Server",
  "version": "0.1.5",
  "transport": "sse",
  "sse_endpoint": "/sse",
  "tools_available": 11,
  "has_valid_tokens": true
}
```

### Prometheus Monitoring

```yaml
podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

## 🔄 Upgrades

### Rolling Updates

```bash
# Update image tag
helm upgrade slack-mcp . \
  --namespace mcp-servers \
  --set image.tag=0.1.5 \
  --reuse-values

# Check rollout status
kubectl rollout status deployment/slack-mcp-server -n mcp-servers
```

### Blue-Green Deployment

```bash
# Deploy new version alongside existing
helm install slack-mcp-v2 . \
  --namespace mcp-servers \
  --set nameOverride=slack-mcp-v2 \
  --set image.tag=0.1.5

# Test new version
kubectl port-forward -n mcp-servers service/slack-mcp-v2 8001:8000

# Switch traffic (update ingress/service selector)
# Remove old version
helm uninstall slack-mcp -n mcp-servers
```

## 🐛 Troubleshooting

### Common Issues

#### Pod CrashLoopBackOff

```bash
# Check logs
kubectl logs -n mcp-servers deployment/slack-mcp-server

# Common causes:
# - Invalid Slack tokens
# - Missing environment variables
# - Resource limits too low
```

#### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n mcp-servers

# Check if pods are ready
kubectl get pods -n mcp-servers -o wide

# Test internal connectivity
kubectl run debug --image=busybox -it --rm -- wget -qO- http://slack-mcp-server:8000/health
```

#### Health Check Failures

```bash
# Check probe configuration
kubectl describe pod -n mcp-servers <pod-name>

# Test health endpoint manually
kubectl exec -n mcp-servers <pod-name> -- curl localhost:8000/health
```

### Debug Mode

```bash
# Enable debug logging
helm upgrade slack-mcp . \
  --namespace mcp-servers \
  --set env[0].name=LOG_LEVEL \
  --set env[0].value=DEBUG \
  --reuse-values
```

## 📚 Additional Resources

- [Helm Chart README](README.md)
- [Slack MCP Server Documentation](../README.md)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)

---

For more help, visit our [GitHub Issues](https://github.com/bluefoxlabsai/bfl-mcp-servers/issues) page.
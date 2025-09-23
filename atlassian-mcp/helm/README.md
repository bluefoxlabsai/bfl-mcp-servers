# Atlassian MCP Server Helm Chart

This Helm chart deploys the Atlassian MCP (Model Context Protocol) server to Kubernetes, providing Jira and Confluence integration capabilities.

## Features

- **Jira Integration**: Create, read, update issues, manage projects and workflows
- **Confluence Integration**: Create, read, update pages and spaces
- **Multiple Transport Protocols**: Support for stdio and SSE (Server-Sent Events) protocols
- **Kubernetes Native**: Full Kubernetes deployment with proper secret management
- **Interactive Installation Script**: Easy setup with prompts for credentials
- **Safe Uninstall Script**: Clean removal with dry-run and safety checks
- **Auto-scaling**: HPA support for handling varying loads
- **Health Monitoring**: Built-in health checks and observability

## Important Note

The Atlassian MCP server supports two transport protocols:
- **stdio**: Traditional MCP communication via kubectl exec (interactive mode)
- **sse**: Server-sent events transport for HTTP-based integrations (recommended)

This chart is configured to use SSE transport by default, which provides better performance and is suitable for HTTP-based MCP client integrations.

## Prerequisites

- Kubernetes 1.16+
- Helm 3.2.0+
- Valid Jira and/or Confluence credentials (API tokens or personal access tokens)

## Installation

### Quick Start with Installation Script

The easiest way to install the chart is using the interactive installation script:

```bash
./install.sh
```

The script will prompt you for:
- Kubernetes namespace (defaults to `default`)
- Confluence URL and API token
- Jira URL and API token

You can also set environment variables to skip some prompts:
```bash
NAMESPACE=atlassian CONFLUENCE_URL=https://company.atlassian.net ./install.sh my-release-name
```

### Manual Installation

1. **Create namespace (optional)**:
   ```bash
   kubectl create namespace atlassian
   ```

2. **Create a values file with your credentials**:
   ```bash
   cat > my-values.yaml << EOF
   secret:
     create: true
     confluenceUrl: "https://your-company.atlassian.net"
     confluenceUsername: "your-email@company.com"
     confluenceApiToken: "your-confluence-api-token"
     jiraUrl: "https://your-company.atlassian.net"
     jiraUsername: "your-email@company.com"
     jiraApiToken: "your-jira-api-token"
   EOF
   ```

3. **Install the chart**:
   ```bash
   helm install atlassian-mcp . \
     --namespace atlassian \
     --create-namespace \
     -f my-values.yaml
   ```

4. **Get service information**:
   ```bash
   kubectl get svc --namespace atlassian
   ```

### STDIO Transport (Interactive Mode)

For kubectl exec-based access:

```bash
# Install with stdio transport
helm install atlassian-mcp . \
  --namespace atlassian \
  --create-namespace \
  --set mcp.transport="stdio" \
  -f my-values.yaml

# Connect to MCP server
export POD_NAME=$(kubectl get pods --namespace atlassian -l "app.kubernetes.io/name=atlassian-mcp" -o jsonpath="{.items[0].metadata.name}")
kubectl exec -it $POD_NAME --namespace atlassian -- uv run mcp-atlassian
```

## Configuration Options

### Required Configuration

| Parameter | Description | Example |
|-----------|-------------|---------|
| `secret.confluenceUrl` | Confluence base URL | `https://company.atlassian.net` |
| `secret.confluenceApiToken` | Confluence API token | `ATATT3xFfGF0...` |
| `secret.jiraUrl` | Jira base URL | `https://company.atlassian.net` |
| `secret.jiraApiToken` | Jira API token | `ATATT3xFfGF0...` |

### Optional Configuration

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `mcp.transport` | Transport protocol | `sse` | `stdio`, `sse` |
| `image.repository` | Container image | `bfljerum/atlassian-mcp` | - |
| `image.tag` | Image tag | `latest` | - |
| `service.enabled` | Enable Kubernetes service | `auto` | `true`, `false`, `auto` |
| `secret.readOnlyMode` | Read-only operations | `false` | `true`, `false` |
| `secret.confluenceSpacesFilter` | Filter Confluence spaces | `""` | Comma-separated list |
| `secret.jiraProjectsFilter` | Filter Jira projects | `""` | Comma-separated list |

### MCP Client Integration

#### For MCP Clients (SSE Transport)

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "atlassian-mcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-stdio", "sse://your-service:8000"]
    }
  }
}
```

#### For Claude Desktop

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "kubectl",
      "args": ["exec", "-i", "pod-name", "--", "uv", "run", "mcp-atlassian"]
    }
  }
}
```

### Installation with Custom Values

1. **Create a comprehensive values file**:
   ```yaml
   # my-values.yaml
   secret:
     create: true
     # Confluence Configuration
     confluenceUrl: "https://your-company.atlassian.net"
     confluenceUsername: "your-email@company.com"
     confluenceApiToken: "ATATT3xFfGF0..."
     confluenceSslVerify: "true"
     confluenceSpacesFilter: "SPACE1,SPACE2"  # Optional: limit to specific spaces
     
     # Jira Configuration  
     jiraUrl: "https://your-company.atlassian.net"
     jiraUsername: "your-email@company.com"
     jiraApiToken: "ATATT3xFfGF0..."
     jiraSslVerify: "true"
     jiraProjectsFilter: "PROJ1,PROJ2"  # Optional: limit to specific projects
     
     # Optional Settings
     readOnlyMode: "false"
     verboseLogging: "true"

   # Resource configuration
   resources:
     limits:
       cpu: 1000m
       memory: 1Gi
     requests:
       cpu: 200m
       memory: 256Mi

   # Auto-scaling
   autoscaling:
     enabled: true
     minReplicas: 1
     maxReplicas: 5
     targetCPUUtilizationPercentage: 70

   # Ingress for external access
   ingress:
     enabled: true
     hosts:
       - host: atlassian-mcp.example.com
   ```

2. **Install with custom values**:
   ```bash
   helm install atlassian-mcp . -f my-values.yaml
   ```

### Security Configuration

#### API Token Generation

1. **Generate Atlassian API Token**:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Copy the generated token (works for both Jira and Confluence)

2. **Test Your Credentials**:
   ```bash
   # Test Jira access
   curl -u your-email@company.com:your-api-token \
     https://your-company.atlassian.net/rest/api/3/myself
   
   # Test Confluence access
   curl -u your-email@company.com:your-api-token \
     https://your-company.atlassian.net/wiki/rest/api/user/current
   ```
## Monitoring and Troubleshooting

### Health Checks

For SSE transport, the server provides a health endpoint:

```bash
# Port-forward to access health endpoint
kubectl port-forward service/atlassian-mcp 8080:8000 --namespace atlassian
curl http://localhost:8080/health
```

### Viewing Logs

```bash
# View all logs
kubectl logs -l app.kubernetes.io/name=atlassian-mcp --namespace atlassian

# Follow logs in real-time
kubectl logs -f deployment/atlassian-mcp --namespace atlassian

# View logs for specific pod
kubectl logs pod-name --namespace atlassian
```

### Common Troubleshooting

#### Authentication Issues

```bash
# Check if secrets are properly mounted
kubectl exec -it deployment/atlassian-mcp -- env | grep -E "(CONFLUENCE|JIRA)"

# Test credentials manually
kubectl exec -it deployment/atlassian-mcp -- curl -u email:token https://company.atlassian.net/rest/api/3/myself
```

#### Network Connectivity

```bash
# Test DNS resolution
kubectl exec -it deployment/atlassian-mcp -- nslookup company.atlassian.net

# Test HTTPS connectivity
kubectl exec -it deployment/atlassian-mcp -- curl -I https://company.atlassian.net
```

#### Performance Issues

```bash
# Check resource usage
kubectl top pods --namespace atlassian

# Check if HPA is working
kubectl get hpa --namespace atlassian

# Scale manually if needed
kubectl scale deployment atlassian-mcp --replicas=3 --namespace atlassian
### Uninstallation

#### Using the Uninstall Script (Recommended)

The easiest way to uninstall is using the provided script:

```bash
# Interactive uninstallation (will prompt for confirmation)
./uninstall.sh

# Uninstall specific release
./uninstall.sh my-atlassian-mcp

# Dry run to see what would be deleted
./uninstall.sh --dry-run

# Uninstall but keep the namespace
./uninstall.sh --keep-namespace

# Non-interactive with environment variable
NAMESPACE=mcp-servers ./uninstall.sh atlassian-mcp
```

#### Manual Uninstallation

Alternatively, use Helm directly:

```bash
# Uninstall the release
helm uninstall atlassian-mcp --namespace mcp-servers

# Optional: Delete the namespace if empty
kubectl delete namespace mcp-servers
```

The uninstall script provides additional safety features:
- ✅ **Safety checks** - Verifies release exists before deletion
- 🔍 **Dry-run mode** - Preview deletions before execution
- 🏷️ **Namespace cleanup** - Automatically removes empty namespaces
- 📋 **Confirmation prompts** - Prevents accidental deletions

## Available MCP Tools

The Atlassian MCP server provides the following tools:

### Jira Tools
- `jira_create_issue` - Create new Jira issues
- `jira_get_issue` - Retrieve issue details
- `jira_update_issue` - Update existing issues  
- `jira_search_issues` - Search issues with JQL
- `jira_get_projects` - List available projects
- `jira_get_issue_types` - Get issue types for a project
- `jira_get_statuses` - Get available statuses
- `jira_transition_issue` - Change issue status
- `jira_add_comment` - Add comments to issues

### Confluence Tools
- `confluence_create_page` - Create new pages
- `confluence_get_page` - Retrieve page content
- `confluence_update_page` - Update existing pages
- `confluence_search_pages` - Search pages by title/content
- `confluence_get_spaces` - List available spaces
- `confluence_get_page_tree` - Get page hierarchy

## Examples

### Creating a Jira Issue

```bash
# Connect to MCP server
kubectl exec -it deployment/atlassian-mcp -- uv run mcp-atlassian

# Use the jira_create_issue tool
{
  "project": "PROJ1",
  "summary": "New feature request",
  "description": "Detailed description here",
  "issueType": "Story"
}
```

### Creating a Confluence Page

```bash
# Use the confluence_create_page tool
{
  "space": "DOCS", 
  "title": "New Documentation Page",
  "content": "<p>Page content in HTML format</p>",
  "parentPageId": "12345"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test with your Atlassian instance
4. Submit a pull request

## Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review Atlassian API documentation for rate limits and permissions


## Upgrading

```bash
# Upgrade with new values
helm upgrade atlassian-mcp . -f my-values.yaml --namespace atlassian

# Check rollout status
kubectl rollout status deployment/atlassian-mcp --namespace atlassian
```

## Advanced Topics

### Custom Environment Variables

Add custom environment variables:

```yaml
extraEnvVars:
  - name: MCP_TIMEOUT
    value: "30"
  - name: MCP_VERBOSE  
    value: "true"
```

### Network Policies

Enable network policies for additional security:

```yaml
networkPolicy:
  enabled: true
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: mcp-clients
```

### Persistent Storage

If you need persistent storage for caching:

```yaml
persistence:
  enabled: true
  size: 1Gi
  storageClass: fast-ssd
```

## License

This Helm chart is released under the MIT License.
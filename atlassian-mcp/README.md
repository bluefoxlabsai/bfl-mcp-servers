# MCP Atlassian

![PyPI Version](https://img.shields.io/pypi/v/mcp-atlassian)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mcp-atlassian)
![PePy - Total Downloads](https://static.pepy.tech/personalized-badge/mcp-atlassian?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Total%20Downloads)
[![Docker Pulls](https://img.shields.io/docker/pulls/bfljerum/atlassian-mcp)](https://hub.docker.com/r/bfljerum/atlassian-mcp)
[![Run Tests](https://github.com/sooperset/mcp-atlassian/actions/workflows/tests.yml/badge.svg)](https://github.com/sooperset/mcp-atlassian/actions/workflows/tests.yml)
![License](https://img.shields.io/github/license/sooperset/mcp-atlassian)

**Model Context Protocol (MCP) server for Atlassian products** - Connect AI assistants to your Confluence and Jira instances with comprehensive support for both Cloud and Server/Data Center deployments.

## ✨ Features

- **📝 Automatic Jira Updates** - "Update Jira from our meeting notes"
- **🔍 AI-Powered Confluence Search** - "Find our OKR guide in Confluence and summarize it"
- **🐛 Smart Issue Management** - "Show me urgent bugs in PROJ project from last week"
- **📄 Content Creation** - "Create a tech design doc for XYZ feature"

### Compatibility Matrix

| Product        | Cloud | Server/Data Center |
|----------------|-------|--------------------|
| **Confluence** | ✅    | ✅ (6.0+)           |
| **Jira**       | ✅    | ✅ (8.14+)          |

## 📦 Available Deployment Options

[![Docker Hub](https://img.shields.io/docker/v/bfljerum/atlassian-mcp?label=Docker%20Hub&style=for-the-badge&logo=docker)](https://hub.docker.com/r/bfljerum/atlassian-mcp)
[![PyPI](https://img.shields.io/pypi/v/mcp-atlassian?label=PyPI&style=for-the-badge&logo=python)](https://pypi.org/project/mcp-atlassian/)

- **🐳 Docker Image**: `bfljerum/atlassian-mcp:latest` (Multi-platform: AMD64, ARM64)
- **🐍 Python Package**: `pip install mcp-atlassian` 
- **☸️ Kubernetes**: Production-ready Helm chart with interactive installer in `/helm` directory
- **💻 Local Development**: Clone and run with UV

## 🚀 Quick Start

### Prerequisites

- **Atlassian Instance**: Cloud or Server/Data Center
- **API Credentials**: API Token (Cloud) or Personal Access Token (Server/DC)
- **Docker** or **Python 3.10+** with **UV**

### 1. Get Your API Credentials

#### For Atlassian Cloud (Recommended)
1. Go to [API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token** and name it
3. Copy the token immediately

#### For Server/Data Center
1. Go to **Profile** → **Personal Access Tokens**
2. Click **Create token**, set name and expiry
3. Copy the token immediately

### 2. Choose Your Deployment Method

## 🐳 Docker Deployment

### Run with Docker

```bash
# Pull the official image from Docker Hub
docker pull bfljerum/atlassian-mcp:latest

# Run with your credentials
docker run --rm -p 8000:8000 \
  -e CONFLUENCE_URL="https://your-company.atlassian.net/wiki" \
  -e CONFLUENCE_USERNAME="your.email@company.com" \
  -e CONFLUENCE_API_TOKEN="your_confluence_api_token" \
  -e JIRA_URL="https://your-company.atlassian.net" \
  -e JIRA_USERNAME="your.email@company.com" \
  -e JIRA_API_TOKEN="your_jira_api_token" \
  bfljerum/atlassian-mcp:latest

# Or use environment file
docker run --rm -p 8000:8000 --env-file .env \
  bfljerum/atlassian-mcp:latest
```

### Multi-Platform Support

The Docker image supports multiple Linux architectures:
- **Linux AMD64** (Intel/AMD processors)
- **Linux ARM64** (Apple Silicon, ARM servers)

```bash
# Verify multi-platform support
docker buildx imagetools inspect bfljerum/atlassian-mcp:latest
```

### Build Local Docker Image

```bash
# Clone and build
git clone <repository-url>
cd atlassian-mcp
docker build -t atlassian-mcp .

# Run locally built image
docker run --rm -p 8000:8000 --env-file .env atlassian-mcp
```

### Test Docker Deployment

```bash
# Test help command
docker run --rm bfljerum/atlassian-mcp:latest --help

# Test SSE endpoint
curl -N http://localhost:8000/sse

# Health check
curl http://localhost:8000/health
```

### Performance Features

- **🚀 Fast Startup**: Optimized container starts instantly without rebuilding
- **📦 Minimal Size**: Alpine Linux base with only essential components  
- **🔒 Secure**: Runs as non-root user (UID: 1000)
- **🌍 Multi-platform**: Supports AMD64 and ARM64 Linux architectures

## 💻 Local Development with UV

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd atlassian-mcp

# Install dependencies with UV
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env with your Atlassian credentials
```

### Run Locally

```bash
# STDIO mode (for MCP clients like Claude Desktop)
uv run mcp-atlassian

# SSE mode (for web/HTTP clients)
uv run mcp-atlassian --transport sse --host 0.0.0.0 --port 8000

# With verbose logging
uv run mcp-atlassian --transport sse --verbose --host 0.0.0.0 --port 8000

# View all options
uv run mcp-atlassian --help
```

### Available Commands

| Command | Description |
|---------|-------------|
| `uv run mcp-atlassian` | Start in STDIO mode (default) |
| `uv run mcp-atlassian --transport sse` | Start HTTP server with SSE |
| `uv run mcp-atlassian --verbose` | Enable verbose logging |
| `uv run mcp-atlassian --read-only` | Enable read-only mode |
| `uv run mcp-atlassian --help` | Show all available options |

## ☸️ Kubernetes Deployment

### Helm Chart Installation

A production-ready Helm chart is available in the `/helm` directory for Kubernetes deployments:

```bash
# Quick Installation (Interactive)
cd helm
NAMESPACE=mcp-servers ./install.sh atlassian-mcp

# Test Installation (Dry Run)
NAMESPACE=mcp-servers ./install.sh atlassian-mcp --dry-run

# Non-Interactive Installation (Environment Variables)
NAMESPACE=mcp-servers \
CONFLUENCE_URL=https://your-company.atlassian.net/wiki \
CONFLUENCE_USERNAME=your.email@company.com \
CONFLUENCE_API_TOKEN=your_confluence_token \
JIRA_URL=https://your-company.atlassian.net \
JIRA_USERNAME=your.email@company.com \
JIRA_API_TOKEN=your_jira_token \
./install.sh atlassian-mcp

# Manual Helm Installation
helm install atlassian-mcp . \
  --namespace mcp-servers --create-namespace \
  --set secret.confluenceUrl=https://your-company.atlassian.net/wiki \
  --set secret.confluenceUsername=your.email@company.com \
  --set-string secret.confluenceApiToken=your_confluence_token \
  --set secret.jiraUrl=https://your-company.atlassian.net \
  --set secret.jiraUsername=your.email@company.com \
  --set-string secret.jiraApiToken=your_jira_token
```

#### Installation Features
- **🔧 Interactive Setup** - Guided credential collection with prompts
- **🧪 Dry-Run Testing** - Validate configuration without deployment  
- **🔒 Secure Credential Handling** - Encrypted Kubernetes secrets
- **📋 Environment Variable Support** - Non-interactive automation-friendly installation
- **✅ Production Ready** - Uses `bfljerum/atlassian-mcp:latest` from Docker Hub

### Accessing the Service

Once deployed, access your MCP server:

```bash
# Port forward to localhost
kubectl --namespace mcp-servers port-forward service/atlassian-mcp 8080:8000

# Test the health endpoint
curl http://localhost:8080/health

# View service logs
kubectl logs -l app.kubernetes.io/name=atlassian-mcp --namespace mcp-servers

# Get service status
kubectl get pods --namespace mcp-servers -l app.kubernetes.io/name=atlassian-mcp
```

#### MCP Client Configuration

For Claude Desktop or other MCP clients, use the SSE transport:

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

### Kubernetes Features

- **� Secure Secret Management** - Atlassian credentials stored as encrypted K8s secrets
- **📊 TCP Health Checks** - Readiness and liveness probes for reliability
- **� SSE Transport** - High-performance Server-Sent Events protocol
- **🔒 Security Hardening** - Non-root containers with restrictive security contexts
- **📱 Multi-Platform Support** - AMD64 and ARM64 compatible containers
- **⚙️ Configurable Resources** - CPU/memory limits and requests
- **📝 Volume Mounting** - Persistent logging directory
- **🌐 Service Discovery** - Kubernetes native service resolution
- **🔄 Optional HPA Support** - Horizontal Pod Autoscaling (configurable)
- **🌐 Optional Ingress/HTTPRoute** - External access configuration (configurable)

### Uninstalling from Kubernetes

To remove the Atlassian MCP server from your Kubernetes cluster:

```bash
# Basic uninstallation (interactive)
cd helm
./uninstall.sh

# Uninstall specific release
./uninstall.sh my-atlassian-mcp

# Dry run - see what would be deleted
./uninstall.sh --dry-run

# Uninstall but keep the namespace
./uninstall.sh --keep-namespace

# Non-interactive uninstallation
NAMESPACE=mcp-servers ./uninstall.sh atlassian-mcp

# Manual Helm uninstall
helm uninstall atlassian-mcp --namespace mcp-servers
kubectl delete namespace mcp-servers  # if desired
```

#### Uninstall Features
- **🔍 Dry-Run Mode** - Preview what will be deleted before actual removal
- **🏷️ Namespace Management** - Automatically cleans up empty namespaces
- **✅ Safety Checks** - Confirms release exists before attempting deletion
- **📋 Confirmation Prompts** - Prevents accidental deletions
- **🔧 Flexible Options** - Keep namespaces or custom release names

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required: Atlassian Instance URLs
JIRA_URL=https://your-company.atlassian.net
CONFLUENCE_URL=https://your-company.atlassian.net/wiki

# Cloud Authentication (API Token)
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_TOKEN=your_confluence_api_token

# Server/Data Center Authentication (Personal Access Token)
JIRA_PERSONAL_TOKEN=your_jira_personal_access_token
CONFLUENCE_PERSONAL_TOKEN=your_confluence_personal_access_token

# Optional Configuration
CONFLUENCE_SPACES_FILTER=DEV,TEAM,DOC  # Filter by space keys
JIRA_PROJECTS_FILTER=PROJ,DEV,SUPPORT  # Filter by project keys
READ_ONLY_MODE=false                    # Enable read-only mode
MCP_VERBOSE=false                       # Enable verbose logging
```

### Example `.env` File

```bash
# Atlassian Cloud Example
JIRA_URL=https://mycompany.atlassian.net
JIRA_USERNAME=john.doe@mycompany.com
JIRA_API_TOKEN=ATATT3xFfGF0T4JL7S1w75ZY...

CONFLUENCE_URL=https://mycompany.atlassian.net/wiki
CONFLUENCE_USERNAME=john.doe@mycompany.com
CONFLUENCE_API_TOKEN=ATATT3xFfGF0T4JL7S1w75ZY...

# Optional filters
CONFLUENCE_SPACES_FILTER=DEV,TEAM
JIRA_PROJECTS_FILTER=PROJ,SUPPORT
```

### Kubernetes Configuration

For Kubernetes deployments, credentials are managed through the `values.yaml` file or Helm install commands. The installation script will securely store these as Kubernetes secrets:

```yaml
# helm/values.yaml (excerpt)
secret:
  # Confluence Configuration
  confluenceUrl: "https://your-company.atlassian.net/wiki"
  confluenceUsername: "your.email@company.com"
  confluenceApiToken: "your_confluence_api_token"
  
  # Jira Configuration  
  jiraUrl: "https://your-company.atlassian.net"
  jiraUsername: "your.email@company.com"
  jiraApiToken: "your_jira_api_token"
```

**⚠️ Security Note**: The `values.yaml` file contains default credentials for development. For production deployments:
1. Use the interactive installer: `./install.sh atlassian-mcp`
2. Or pass credentials via environment variables
3. Never commit real credentials to version control

## 🔗 MCP Client Integration

### Claude Desktop

Add this configuration to your Claude Desktop config file:

**Location:**
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**STDIO Configuration (Local UV):**
```json
{
  "mcpServers": {
    "atlassian": {
      "command": "uv",
      "args": ["run", "mcp-atlassian"],
      "cwd": "/path/to/atlassian-mcp",
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_confluence_api_token",
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_jira_api_token"
      }
    }
  }
}
```

**Docker Configuration:**
```json
{
  "mcpServers": {
    "atlassian": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME", 
        "-e", "CONFLUENCE_API_TOKEN",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_API_TOKEN",
        "bfljerum/atlassian-mcp:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_confluence_api_token",
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_jira_api_token"
      }
    }
  }
}
```

**SSE Configuration (Remote Server):**
```json
{
  "mcpServers": {
    "atlassian": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### Cursor IDE

1. Open **Settings** → **MCP** → **+ Add new global MCP server**
2. Use the same JSON configuration as Claude Desktop
3. Or configure via Cursor's MCP interface

## 🧪 Testing & Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_confluence.py -v
```

### Development Setup

```bash
# Install development dependencies
uv sync --group dev

# Install pre-commit hooks
uv run pre-commit install

# Run linting and formatting
uv run ruff check .
uv run black .
uv run mypy .
```

## 🔧 Advanced Configuration

### Server/Data Center Setup

For on-premises Atlassian deployments:

```bash
# Environment variables for Server/Data Center
CONFLUENCE_URL=https://confluence.your-company.com
CONFLUENCE_PERSONAL_TOKEN=your_confluence_pat
CONFLUENCE_SSL_VERIFY=false  # Only for self-signed certificates

JIRA_URL=https://jira.your-company.com
JIRA_PERSONAL_TOKEN=your_jira_pat
JIRA_SSL_VERIFY=false  # Only for self-signed certificates
```

### Optional Filters

```bash
# Limit access to specific spaces/projects
CONFLUENCE_SPACES_FILTER=DEV,TEAM,DOC
JIRA_PROJECTS_FILTER=PROJ,DEV,SUPPORT

# Enable read-only mode
READ_ONLY_MODE=true

# Enable verbose logging
MCP_VERBOSE=true

# Specify enabled tools (comma-separated)
ENABLED_TOOLS=confluence_search,jira_get_issue,jira_create_issue
```

## 📚 Available Tools

### Confluence Tools
- **confluence_search** - Search pages and content
- **confluence_get_page** - Retrieve specific pages
- **confluence_create_page** - Create new pages
- **confluence_update_page** - Update existing pages
- **confluence_delete_page** - Delete pages
- **confluence_list_spaces** - List available spaces

### Jira Tools
- **jira_search** - Search issues with JQL
- **jira_get_issue** - Get specific issue details
- **jira_create_issue** - Create new issues
- **jira_update_issue** - Update existing issues
- **jira_add_comment** - Add comments to issues
- **jira_transition_issue** - Change issue status
- **jira_list_projects** - List available projects

## 🐛 Troubleshooting

### Common Issues

**Authentication Errors:**
```bash
# Check your credentials
curl -u "email:api_token" https://your-company.atlassian.net/rest/api/3/myself
```

**Connection Issues:**
```bash
# Test Docker connectivity
docker run --rm -e JIRA_URL="$JIRA_URL" -e JIRA_USERNAME="$JIRA_USERNAME" -e JIRA_API_TOKEN="$JIRA_API_TOKEN" bfljerum/atlassian-mcp:latest --help
```

**SSL Certificate Issues (Server/DC):**
```bash
# Disable SSL verification for self-signed certificates
export CONFLUENCE_SSL_VERIFY=false
export JIRA_SSL_VERIFY=false
```

### Debug Mode

```bash
# Enable verbose logging
uv run mcp-atlassian --verbose

# Or with Docker
docker run --rm -p 8000:8000 --env-file .env bfljerum/atlassian-mcp:latest --verbose
```

## 📋 Requirements

- **Python**: 3.10+ (for local development)
- **Docker**: For containerized deployment
- **UV**: Package manager (for local development)
- **Atlassian Access**: Valid API tokens or Personal Access Tokens

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `uv sync --group dev`
4. Make your changes and add tests
5. Run tests: `uv run pytest`
6. Run linting: `uv run pre-commit run --all-files`
7. Submit a pull request

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/sooperset/mcp-atlassian/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sooperset/mcp-atlassian/discussions)
- **Documentation**: Check the `.env.example` file for all configuration options

---

**Ready to connect your AI assistant to Atlassian?** Choose your deployment method above and start automating your Jira and Confluence workflows! 🚀
  }
}
```

> [!NOTE]
> - For the Standard Flow:
>   - `ATLASSIAN_OAUTH_CLOUD_ID` is obtained from the `--oauth-setup` wizard output or is known for your instance.
>   - Other `ATLASSIAN_OAUTH_*` client variables are from your OAuth app in the Atlassian Developer Console.
>   - `JIRA_URL` and `CONFLUENCE_URL` for your Cloud instances are always required.
>   - The volume mount (`-v .../.mcp-atlassian:/home/app/.mcp-atlassian`) is crucial for persisting the OAuth tokens obtained by the wizard, enabling automatic refresh.

**Example for Pre-existing Access Token (BYOT - Bring Your Own Token):**

This configuration is for when you are providing your own externally managed OAuth 2.0 access token.

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "JIRA_URL",
        "-e", "CONFLUENCE_URL",
        "-e", "ATLASSIAN_OAUTH_CLOUD_ID",
        "-e", "ATLASSIAN_OAUTH_ACCESS_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "ATLASSIAN_OAUTH_CLOUD_ID": "YOUR_KNOWN_CLOUD_ID",
        "ATLASSIAN_OAUTH_ACCESS_TOKEN": "YOUR_PRE_EXISTING_OAUTH_ACCESS_TOKEN"
      }
    }
  }
}
```

> [!NOTE]
> - For the BYOT Method:
>   - You primarily need `JIRA_URL`, `CONFLUENCE_URL`, `ATLASSIAN_OAUTH_CLOUD_ID`, and `ATLASSIAN_OAUTH_ACCESS_TOKEN`.
>   - Standard OAuth client variables (`ATLASSIAN_OAUTH_CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`, `SCOPE`) are **not** used.
>   - Token lifecycle (e.g., refreshing the token before it expires and restarting mcp-atlassian) is your responsibility, as the server will not refresh BYOT tokens.

</details>

<details>
<summary>Proxy Configuration</summary>

MCP Atlassian supports routing API requests through standard HTTP/HTTPS/SOCKS proxies. Configure using environment variables:

- Supports standard `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, `SOCKS_PROXY`.
- Service-specific overrides are available (e.g., `JIRA_HTTPS_PROXY`, `CONFLUENCE_NO_PROXY`).
- Service-specific variables override global ones for that service.

Add the relevant proxy variables to the `args` (using `-e`) and `env` sections of your MCP configuration:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "... existing Confluence/Jira vars",
        "-e", "HTTP_PROXY",
        "-e", "HTTPS_PROXY",
        "-e", "NO_PROXY",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "... existing Confluence/Jira vars": "...",
        "HTTP_PROXY": "http://proxy.internal:8080",
        "HTTPS_PROXY": "http://proxy.internal:8080",
        "NO_PROXY": "localhost,.your-company.com"
      }
    }
  }
}
```

Credentials in proxy URLs are masked in logs. If you set `NO_PROXY`, it will be respected for requests to matching hosts.

</details>
<details>
<summary>Custom HTTP Headers Configuration</summary>

MCP Atlassian supports adding custom HTTP headers to all API requests. This feature is particularly useful in corporate environments where additional headers are required for security, authentication, or routing purposes.

Custom headers are configured using environment variables with comma-separated key=value pairs:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME",
        "-e", "CONFLUENCE_API_TOKEN",
        "-e", "CONFLUENCE_CUSTOM_HEADERS",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_API_TOKEN",
        "-e", "JIRA_CUSTOM_HEADERS",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_confluence_api_token",
        "CONFLUENCE_CUSTOM_HEADERS": "X-Confluence-Service=mcp-integration,X-Custom-Auth=confluence-token,X-ALB-Token=secret-token",
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_jira_api_token",
        "JIRA_CUSTOM_HEADERS": "X-Forwarded-User=service-account,X-Company-Service=mcp-atlassian,X-Jira-Client=mcp-integration"
      }
    }
  }
}
```

**Security Considerations:**

- Custom header values are masked in debug logs to protect sensitive information
- Ensure custom headers don't conflict with standard HTTP or Atlassian API headers
- Avoid including sensitive authentication tokens in custom headers if already using basic auth or OAuth
- Headers are sent with every API request - verify they don't interfere with API functionality

</details>


<details>
<summary>Multi-Cloud OAuth Support</summary>

MCP Atlassian supports multi-cloud OAuth scenarios where each user connects to their own Atlassian cloud instance. This is useful for multi-tenant applications, chatbots, or services where users provide their own OAuth tokens.

**Minimal OAuth Configuration:**

1. Enable minimal OAuth mode (no client credentials required):
   ```bash
   docker run -e ATLASSIAN_OAUTH_ENABLE=true -p 9000:9000 \
     ghcr.io/sooperset/mcp-atlassian:latest \
     --transport streamable-http --port 9000
   ```

2. Users provide authentication via HTTP headers:
   - `Authorization: Bearer <user_oauth_token>`
   - `X-Atlassian-Cloud-Id: <user_cloud_id>`

**Example Integration (Python):**
```python
import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

user_token = "user-specific-oauth-token"
user_cloud_id = "user-specific-cloud-id"

async def main():
    # Connect to streamable HTTP server with custom headers
    async with streamablehttp_client(
        "http://localhost:9000/mcp",
        headers={
            "Authorization": f"Bearer {user_token}",
            "X-Atlassian-Cloud-Id": user_cloud_id
        }
    ) as (read_stream, write_stream, _):
        # Create a session using the client streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # Example: Get a Jira issue
            result = await session.call_tool(
                "jira_get_issue",
                {"issue_key": "PROJ-123"}
            )
            print(result)

asyncio.run(main())
```

**Configuration Notes:**
- Each request can use a different cloud instance via the `X-Atlassian-Cloud-Id` header
- User tokens are isolated per request - no cross-tenant data leakage
- Falls back to global `ATLASSIAN_OAUTH_CLOUD_ID` if header not provided
- Compatible with standard OAuth 2.0 bearer token authentication

</details>

<details> <summary>Single Service Configurations</summary>

**For Confluence Cloud only:**

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME",
        "-e", "CONFLUENCE_API_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

For Confluence Server/DC, use:
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_PERSONAL_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://confluence.your-company.com",
        "CONFLUENCE_PERSONAL_TOKEN": "your_personal_token"
      }
    }
  }
}
```

**For Jira Cloud only:**

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_API_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

For Jira Server/DC, use:
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "JIRA_URL",
        "-e", "JIRA_PERSONAL_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "https://jira.your-company.com",
        "JIRA_PERSONAL_TOKEN": "your_personal_token"
      }
    }
  }
}
```

</details>

### 👥 HTTP Transport Configuration

Instead of using `stdio`, you can run the server as a persistent HTTP service using either:
- `sse` (Server-Sent Events) transport at `/sse` endpoint
- `streamable-http` transport at `/mcp` endpoint

Both transport types support single-user and multi-user authentication:

**Authentication Options:**
- **Single-User**: Use server-level authentication configured via environment variables
- **Multi-User**: Each user provides their own authentication:
  - Cloud: OAuth 2.0 Bearer tokens
  - Server/Data Center: Personal Access Tokens (PATs)

<details> <summary>Basic HTTP Transport Setup</summary>

1. Start the server with your chosen transport:

    ```bash
    # For SSE transport
    docker run --rm -p 9000:9000 \
      --env-file /path/to/your/.env \
      ghcr.io/sooperset/mcp-atlassian:latest \
      --transport sse --port 9000 -vv

    # OR for streamable-http transport
    docker run --rm -p 9000:9000 \
      --env-file /path/to/your/.env \
      ghcr.io/sooperset/mcp-atlassian:latest \
      --transport streamable-http --port 9000 -vv
    ```

2. Configure your IDE (single-user example):

    **SSE Transport Example:**
    ```json
    {
      "mcpServers": {
        "mcp-atlassian-http": {
          "url": "http://localhost:9000/sse"
        }
      }
    }
    ```

    **Streamable-HTTP Transport Example:**
    ```json
    {
      "mcpServers": {
        "mcp-atlassian-service": {
          "url": "http://localhost:9000/mcp"
        }
      }
    }
    ```
</details>

<details> <summary>Multi-User Authentication Setup</summary>

Here's a complete example of setting up multi-user authentication with streamable-HTTP transport:

1. First, run the OAuth setup wizard to configure the server's OAuth credentials:
   ```bash
   docker run --rm -i \
     -p 8080:8080 \
     -v "${HOME}/.mcp-atlassian:/home/app/.mcp-atlassian" \
     ghcr.io/sooperset/mcp-atlassian:latest --oauth-setup -v
   ```

2. Start the server with streamable-HTTP transport:
   ```bash
   docker run --rm -p 9000:9000 \
     --env-file /path/to/your/.env \
     ghcr.io/sooperset/mcp-atlassian:latest \
     --transport streamable-http --port 9000 -vv
   ```

3. Configure your IDE's MCP settings:

**Choose the appropriate Authorization method for your Atlassian deployment:**

- **Cloud (OAuth 2.0):** Use this if your organization is on Atlassian Cloud and you have an OAuth access token for each user.
- **Server/Data Center (PAT):** Use this if you are on Atlassian Server or Data Center and each user has a Personal Access Token (PAT).

**Cloud (OAuth 2.0) Example:**
```json
{
  "mcpServers": {
    "mcp-atlassian-service": {
      "url": "http://localhost:9000/mcp",
      "headers": {
        "Authorization": "Bearer <USER_OAUTH_ACCESS_TOKEN>"
      }
    }
  }
}
```

**Server/Data Center (PAT) Example:**
```json
{
  "mcpServers": {
    "mcp-atlassian-service": {
      "url": "http://localhost:9000/mcp",
      "headers": {
        "Authorization": "Token <USER_PERSONAL_ACCESS_TOKEN>"
      }
    }
  }
}
```

4. Required environment variables in `.env`:
   ```bash
   JIRA_URL=https://your-company.atlassian.net
   CONFLUENCE_URL=https://your-company.atlassian.net/wiki
   ATLASSIAN_OAUTH_CLIENT_ID=your_oauth_app_client_id
   ATLASSIAN_OAUTH_CLIENT_SECRET=your_oauth_app_client_secret
   ATLASSIAN_OAUTH_REDIRECT_URI=http://localhost:8080/callback
   ATLASSIAN_OAUTH_SCOPE=read:jira-work write:jira-work read:confluence-content.all write:confluence-content offline_access
   ATLASSIAN_OAUTH_CLOUD_ID=your_cloud_id_from_setup_wizard
   ```

> [!NOTE]
> - The server should have its own fallback authentication configured (e.g., via environment variables for API token, PAT, or its own OAuth setup using --oauth-setup). This is used if a request doesn't include user-specific authentication.
> - **OAuth**: Each user needs their own OAuth access token from your Atlassian OAuth app.
> - **PAT**: Each user provides their own Personal Access Token.
> - **Multi-Cloud**: For OAuth users, optionally include `X-Atlassian-Cloud-Id` header to specify which Atlassian cloud instance to use
> - The server will use the user's token for API calls when provided, falling back to server auth if not
> - User tokens should have appropriate scopes for their needed operations

</details>

## Tools

### Key Tools

#### Jira Tools

- `jira_get_issue`: Get details of a specific issue
- `jira_search`: Search issues using JQL
- `jira_create_issue`: Create a new issue
- `jira_update_issue`: Update an existing issue
- `jira_transition_issue`: Transition an issue to a new status
- `jira_add_comment`: Add a comment to an issue

#### Confluence Tools

- `confluence_search`: Search Confluence content using CQL
- `confluence_get_page`: Get content of a specific page
- `confluence_create_page`: Create a new page
- `confluence_update_page`: Update an existing page

<details> <summary>View All Tools</summary>

| Operation | Jira Tools                          | Confluence Tools               |
|-----------|-------------------------------------|--------------------------------|
| **Read**  | `jira_search`                       | `confluence_search`            |
|           | `jira_get_issue`                    | `confluence_get_page`          |
|           | `jira_get_all_projects`             | `confluence_get_page_children` |
|           | `jira_get_project_issues`           | `confluence_get_comments`      |
|           | `jira_get_worklog`                  | `confluence_get_labels`        |
|           | `jira_get_transitions`              | `confluence_search_user`       |
|           | `jira_search_fields`                |                                |
|           | `jira_get_agile_boards`             |                                |
|           | `jira_get_board_issues`             |                                |
|           | `jira_get_sprints_from_board`       |                                |
|           | `jira_get_sprint_issues`            |                                |
|           | `jira_get_issue_link_types`         |                                |
|           | `jira_batch_get_changelogs`*        |                                |
|           | `jira_get_user_profile`             |                                |
|           | `jira_download_attachments`         |                                |
|           | `jira_get_project_versions`         |                                |
| **Write** | `jira_create_issue`                 | `confluence_create_page`       |
|           | `jira_update_issue`                 | `confluence_update_page`       |
|           | `jira_delete_issue`                 | `confluence_delete_page`       |
|           | `jira_batch_create_issues`          | `confluence_add_label`         |
|           | `jira_add_comment`                  | `confluence_add_comment`       |
|           | `jira_transition_issue`             |                                |
|           | `jira_add_worklog`                  |                                |
|           | `jira_link_to_epic`                 |                                |
|           | `jira_create_sprint`                |                                |
|           | `jira_update_sprint`                |                                |
|           | `jira_create_issue_link`            |                                |
|           | `jira_remove_issue_link`            |                                |
|           | `jira_create_version`               |                                |
|           | `jira_batch_create_versions`        |                                |

</details>

*Tool only available on Jira Cloud

</details>

### Tool Filtering and Access Control

The server provides two ways to control tool access:

1. **Tool Filtering**: Use `--enabled-tools` flag or `ENABLED_TOOLS` environment variable to specify which tools should be available:

   ```bash
   # Via environment variable
   ENABLED_TOOLS="confluence_search,jira_get_issue,jira_search"

   # Or via command line flag
   docker run ... --enabled-tools "confluence_search,jira_get_issue,jira_search" ...
   ```

2. **Read/Write Control**: Tools are categorized as read or write operations. When `READ_ONLY_MODE` is enabled, only read operations are available regardless of `ENABLED_TOOLS` setting.

## Troubleshooting & Debugging

### Common Issues

- **Authentication Failures**:
    - For Cloud: Check your API tokens (not your account password)
    - For Server/Data Center: Verify your personal access token is valid and not expired
    - For older Confluence servers: Some older versions require basic authentication with `CONFLUENCE_USERNAME` and `CONFLUENCE_API_TOKEN` (where token is your password)
- **SSL Certificate Issues**: If using Server/Data Center and encounter SSL errors, set `CONFLUENCE_SSL_VERIFY=false` or `JIRA_SSL_VERIFY=false`
- **Permission Errors**: Ensure your Atlassian account has sufficient permissions to access the spaces/projects
- **Custom Headers Issues**: See the ["Debugging Custom Headers"](#debugging-custom-headers) section below to analyze and resolve issues with custom headers

### Debugging Custom Headers

To verify custom headers are being applied correctly:

1. **Enable Debug Logging**: Set `MCP_VERY_VERBOSE=true` to see detailed request logs
   ```bash
   # In your .env file or environment
   MCP_VERY_VERBOSE=true
   MCP_LOGGING_STDOUT=true
   ```

2. **Check Header Parsing**: Custom headers appear in logs with masked values for security:
   ```
   DEBUG Custom headers applied: {'X-Forwarded-User': '***', 'X-ALB-Token': '***'}
   ```

3. **Verify Service-Specific Headers**: Check logs to confirm the right headers are being used:
   ```
   DEBUG Jira request headers: service-specific headers applied
   DEBUG Confluence request headers: service-specific headers applied
   ```

4. **Test Header Format**: Ensure your header string format is correct:
   ```bash
   # Correct format
   JIRA_CUSTOM_HEADERS=X-Custom=value1,X-Other=value2
   CONFLUENCE_CUSTOM_HEADERS=X-Custom=value1,X-Other=value2

   # Incorrect formats (will be ignored)
   JIRA_CUSTOM_HEADERS="X-Custom=value1,X-Other=value2"  # Extra quotes
   JIRA_CUSTOM_HEADERS=X-Custom: value1,X-Other: value2  # Colon instead of equals
   JIRA_CUSTOM_HEADERS=X-Custom = value1               # Spaces around equals
   ```

**Security Note**: Header values containing sensitive information (tokens, passwords) are automatically masked in logs to prevent accidental exposure.

### Debugging Tools

```bash
# Using MCP Inspector for testing
npx @modelcontextprotocol/inspector uvx mcp-atlassian ...

# For local development version
npx @modelcontextprotocol/inspector uv --directory /path/to/your/mcp-atlassian run mcp-atlassian ...

# View logs
# macOS
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log
# Windows
type %APPDATA%\Claude\logs\mcp*.log | more
```

## Security

- Never share API tokens
- Keep .env files secure and private
- See [SECURITY.md](SECURITY.md) for best practices


# MCP SharePoint

![PyPI Version](https://img.shields.io/pypi/v/mcp-sharepoint)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mcp-sharepoint)
![PePy - Total Downloads](https://static.pepy.tech/personalized-badge/mcp-sharepoint?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Total%20Downloads)
[![Docker Pulls](https://img.shields.io/docker/pulls/bfljerum/sharepoint-mcp)](https://hub.docker.com/r/bfljerum/sharepoint-mcp)
[![Run Tests](https://github.com/sooperset/mcp-sharepoint/actions/workflows/tests.yml/badge.svg)](https://github.com/sooperset/mcp-sharepoint/actions/workflows/tests.yml)
![License](https://img.shields.io/github/license/sooperset/mcp-sharepoint)

**Model Context Protocol (MCP) server for Microsoft SharePoint** - Connect AI assistants to your SharePoint sites with comprehensive support for both SharePoint Online and SharePoint Server deployments.

## ✨ Features

- **📝 Document Management** - "Upload and organize documents in SharePoint"
- **🔍 AI-Powered Content Search** - "Find our project documents and summarize them"
- **📄 List Management** - "Create and manage SharePoint lists and items"
- **🔗 Site Navigation** - "Browse SharePoint sites and libraries"

### Compatibility Matrix

| Product                | Online | Server |
| ---------------------- | ------ | ------ |
| **SharePoint**         | ✅     | ✅     |
| **Document Libraries** | ✅     | ✅     |
| **Lists**              | ✅     | ✅     |

## 📦 Available Deployment Options

[![Docker Hub](https://img.shields.io/docker/v/bfljerum/sharepoint-mcp?label=Docker%20Hub&style=for-the-badge&logo=docker)](https://hub.docker.com/r/bfljerum/sharepoint-mcp)
[![PyPI](https://img.shields.io/pypi/v/mcp-sharepoint?label=PyPI&style=for-the-badge&logo=python)](https://pypi.org/project/mcp-sharepoint/)

- **🐳 Docker Image**: `bfljerum/sharepoint-mcp:latest` (Multi-platform: AMD64, ARM64)
- **🐍 Python Package**: `pip install mcp-sharepoint`
- **☸️ Kubernetes**: Production-ready Helm chart with interactive installer in `/helm` directory
- **💻 Local Development**: Clone and run with UV

## 🚀 Quick Start

### Prerequisites

- **SharePoint Instance**: Online or Server
- **Authentication**: Azure AD App Registration or SharePoint credentials
- **Docker** or **Python 3.10+** with **UV**

### 1. Get Your Authentication Credentials

#### For SharePoint Online (Recommended)

1. Register an Azure AD application
2. Configure API permissions for SharePoint
3. Generate client secret
4. Note your tenant ID and client ID

#### For SharePoint Server

1. Use Windows Authentication or Forms-based authentication
2. Ensure proper permissions on SharePoint sites

### 2. Choose Your Deployment Method

## 🐳 Docker Deployment

### Run with Docker

```bash
# Pull the official image from Docker Hub
docker pull bfljerum/sharepoint-mcp:latest

# Run with your credentials
docker run --rm -p 8000:8000 \
  -e SHAREPOINT_SITE_URL="https://yourtenant.sharepoint.com/sites/yoursite" \
  -e AZURE_CLIENT_ID="your_client_id" \
  -e AZURE_CLIENT_SECRET="your_client_secret" \
  -e AZURE_TENANT_ID="your_tenant_id" \
  bfljerum/sharepoint-mcp:latest

# Or use environment file
docker run --rm -p 8000:8000 --env-file .env \
  bfljerum/sharepoint-mcp:latest
```

### Multi-Platform Support

The Docker image supports multiple Linux architectures:

- **Linux AMD64** (Intel/AMD processors)
- **Linux ARM64** (Apple Silicon, ARM servers)

### Test Docker Deployment

```bash
# Test help command
docker run --rm bfljerum/sharepoint-mcp:latest --help

# Test SSE endpoint
curl -N http://localhost:8000/sse

# Health check
curl http://localhost:8000/health
```

## 💻 Local Development with UV

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd sharepoint-mcp

# Install dependencies with UV
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env with your SharePoint credentials
```

### Run Locally

```bash
# STDIO mode (for MCP clients like Claude Desktop)
uv run mcp-sharepoint

# SSE mode (for web/HTTP clients)
uv run mcp-sharepoint --transport sse --host 0.0.0.0 --port 8000

# With verbose logging
uv run mcp-sharepoint --transport sse --verbose --host 0.0.0.0 --port 8000

# View all options
uv run mcp-sharepoint --help
```

## ☸️ Kubernetes Deployment

### Helm Chart Installation

A production-ready Helm chart is available in the `/helm` directory for Kubernetes deployments:

```bash
# Quick Installation (Interactive)
cd helm
NAMESPACE=mcp-servers ./install.sh sharepoint-mcp

# Test Installation (Dry Run)
NAMESPACE=mcp-servers ./install.sh sharepoint-mcp --dry-run

# Non-Interactive Installation (Environment Variables)
NAMESPACE=mcp-servers \
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite \
AZURE_CLIENT_ID=your_client_id \
AZURE_CLIENT_SECRET=your_client_secret \
AZURE_TENANT_ID=your_tenant_id \
./install.sh sharepoint-mcp
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required: SharePoint Configuration
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite

# Azure AD Authentication
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
AZURE_TENANT_ID=your_tenant_id

# Optional Configuration
READ_ONLY_MODE=false                    # Enable read-only mode
MCP_VERBOSE=false                       # Enable verbose logging
```

## 🔗 MCP Client Integration

### Claude Desktop

Add this configuration to your Claude Desktop config file:

**STDIO Configuration (Local UV):**

```json
{
  "mcpServers": {
    "sharepoint": {
      "command": "uv",
      "args": ["run", "mcp-sharepoint"],
      "cwd": "/path/to/sharepoint-mcp",
      "env": {
        "SHAREPOINT_SITE_URL": "https://yourtenant.sharepoint.com/sites/yoursite",
        "AZURE_CLIENT_ID": "your_client_id",
        "AZURE_CLIENT_SECRET": "your_client_secret",
        "AZURE_TENANT_ID": "your_tenant_id"
      }
    }
  }
}
```

**Docker Configuration:**

```json
{
  "mcpServers": {
    "sharepoint": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e",
        "SHAREPOINT_SITE_URL",
        "-e",
        "AZURE_CLIENT_ID",
        "-e",
        "AZURE_CLIENT_SECRET",
        "-e",
        "AZURE_TENANT_ID",
        "bfljerum/sharepoint-mcp:latest"
      ],
      "env": {
        "SHAREPOINT_SITE_URL": "https://yourtenant.sharepoint.com/sites/yoursite",
        "AZURE_CLIENT_ID": "your_client_id",
        "AZURE_CLIENT_SECRET": "your_client_secret",
        "AZURE_TENANT_ID": "your_tenant_id"
      }
    }
  }
}
```

**SSE Configuration (Remote Server):**

```json
{
  "mcpServers": {
    "sharepoint": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## 📚 Available Tools

### SharePoint Tools

- **sharepoint_search** - Search documents and content
- **sharepoint_get_file** - Retrieve specific files
- **sharepoint_upload_file** - Upload new files
- **sharepoint_create_folder** - Create new folders
- **sharepoint_list_items** - List items in libraries/lists
- **sharepoint_create_list_item** - Create new list items
- **sharepoint_update_list_item** - Update existing list items
- **sharepoint_get_site_info** - Get site information

## 🐛 Troubleshooting

### Common Issues

**Authentication Errors:**

```bash
# Check your Azure AD app permissions
# Ensure SharePoint API permissions are granted
```

**Connection Issues:**

```bash
# Test Docker connectivity
docker run --rm -e SHAREPOINT_SITE_URL="$SHAREPOINT_SITE_URL" -e AZURE_CLIENT_ID="$AZURE_CLIENT_ID" bfljerum/sharepoint-mcp:latest --help
```

### Debug Mode

```bash
# Enable verbose logging
uv run mcp-sharepoint --verbose

# Or with Docker
docker run --rm -p 8000:8000 --env-file .env bfljerum/sharepoint-mcp:latest --verbose
```

## 📋 Requirements

- **Python**: 3.10+ (for local development)
- **Docker**: For containerized deployment
- **UV**: Package manager (for local development)
- **SharePoint Access**: Valid Azure AD credentials or SharePoint permissions

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

- **Issues**: [GitHub Issues](https://github.com/sooperset/mcp-sharepoint/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sooperset/mcp-sharepoint/discussions)
- **Documentation**: Check the `.env.example` file for all configuration options

---

**Ready to connect your AI assistant to SharePoint?** Choose your deployment method above and start automating your SharePoint workflows! 🚀

# MCP Teams

![PyPI Version](https://img.shields.io/pypi/v/mcp-teams)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mcp-teams)
![PePy - Total Downloads](https://static.pepy.tech/personalized-badge/mcp-teams?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Total%20Downloads)
[![Docker Pulls](https://img.shields.io/docker/pulls/bfljerum/teams-mcp)](https://hub.docker.com/r/bfljerum/teams-mcp)
[![Run Tests](https://github.com/sooperset/mcp-teams/actions/workflows/tests.yml/badge.svg)](https://github.com/sooperset/mcp-teams/actions/workflows/tests.yml)
![License](https://img.shields.io/github/license/sooperset/mcp-teams)

**Model Context Protocol (MCP) server for Microsoft Teams** - Connect AI assistants to your Microsoft Teams environment with comprehensive support for Teams messaging, channels, meetings, and collaboration features.

## ✨ Features

- **💬 Team Communication** - "Send messages to Teams channels and chats"
- **🔍 AI-Powered Search** - "Find conversations and files across Teams"
- **📅 Meeting Management** - "Schedule and manage Teams meetings"
- **👥 Team Collaboration** - "Manage teams, channels, and memberships"

### Compatibility Matrix

| Product              | Online | Government Cloud |
|---------------------|--------|------------------|
| **Microsoft Teams** | ✅     | ✅               |
| **Teams Chat**      | ✅     | ✅               |
| **Teams Channels**  | ✅     | ✅               |
| **Teams Meetings**  | ✅     | ✅               |

## 📦 Available Deployment Options

[![Docker Hub](https://img.shields.io/docker/v/bfljerum/teams-mcp?label=Docker%20Hub&style=for-the-badge&logo=docker)](https://hub.docker.com/r/bfljerum/teams-mcp)
[![PyPI](https://img.shields.io/pypi/v/mcp-teams?label=PyPI&style=for-the-badge&logo=python)](https://pypi.org/project/mcp-teams/)

- **🐳 Docker Image**: `bfljerum/teams-mcp:latest` (Multi-platform: AMD64, ARM64)
- **🐍 Python Package**: `pip install mcp-teams` 
- **☸️ Kubernetes**: Production-ready Helm chart with interactive installer in `/helm` directory
- **💻 Local Development**: Clone and run with UV

## 🚀 Quick Start

### Prerequisites

- **Microsoft Teams**: Access to Microsoft Teams
- **Azure AD App Registration**: App with Teams API permissions
- **Docker** or **Python 3.10+** with **UV**

### 1. Get Your Authentication Credentials

#### For Microsoft Teams (Recommended)
1. Register an Azure AD application
2. Configure Microsoft Graph API permissions for Teams
3. Generate client secret
4. Note your tenant ID and client ID

### 2. Choose Your Deployment Method

## 🐳 Docker Deployment

### Run with Docker

```bash
# Pull the official image from Docker Hub
docker pull bfljerum/teams-mcp:latest

# Run with your credentials
docker run --rm -p 8000:8000 \
  -e AZURE_CLIENT_ID="your_client_id" \
  -e AZURE_CLIENT_SECRET="your_client_secret" \
  -e AZURE_TENANT_ID="your_tenant_id" \
  bfljerum/teams-mcp:latest

# Or use environment file
docker run --rm -p 8000:8000 --env-file .env \
  bfljerum/teams-mcp:latest
```

### Multi-Platform Support

The Docker image supports multiple Linux architectures:
- **Linux AMD64** (Intel/AMD processors)
- **Linux ARM64** (Apple Silicon, ARM servers)

### Test Docker Deployment

```bash
# Test help command
docker run --rm bfljerum/teams-mcp:latest --help

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
cd teams-mcp

# Install dependencies with UV
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env with your Teams credentials
```

### Run Locally

```bash
# STDIO mode (for MCP clients like Claude Desktop)
uv run mcp-teams

# SSE mode (for web/HTTP clients)
uv run mcp-teams --transport sse --host 0.0.0.0 --port 8000

# With verbose logging
uv run mcp-teams --transport sse --verbose --host 0.0.0.0 --port 8000

# View all options
uv run mcp-teams --help
```

## ☸️ Kubernetes Deployment

### Helm Chart Installation

A production-ready Helm chart is available in the `/helm` directory for Kubernetes deployments:

```bash
# Quick Installation (Interactive)
cd helm
NAMESPACE=mcp-servers ./install.sh teams-mcp

# Test Installation (Dry Run)
NAMESPACE=mcp-servers ./install.sh teams-mcp --dry-run

# Non-Interactive Installation (Environment Variables)
NAMESPACE=mcp-servers \
AZURE_CLIENT_ID=your_client_id \
AZURE_CLIENT_SECRET=your_client_secret \
AZURE_TENANT_ID=your_tenant_id \
./install.sh teams-mcp
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required: Azure AD Authentication
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
    "teams": {
      "command": "uv",
      "args": ["run", "mcp-teams"],
      "cwd": "/path/to/teams-mcp",
      "env": {
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
    "teams": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "AZURE_CLIENT_ID", 
        "-e", "AZURE_CLIENT_SECRET",
        "-e", "AZURE_TENANT_ID",
        "bfljerum/teams-mcp:latest"
      ],
      "env": {
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
    "teams": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## 📚 Available Tools

### Teams Communication Tools
- **teams_send_message** - Send messages to channels or chats
- **teams_get_messages** - Retrieve messages from channels or chats
- **teams_search_messages** - Search across Teams conversations
- **teams_reply_to_message** - Reply to specific messages

### Teams Management Tools
- **teams_list_teams** - List all teams user has access to
- **teams_get_team_info** - Get detailed team information
- **teams_list_channels** - List channels in a team
- **teams_create_channel** - Create new channels
- **teams_get_channel_info** - Get channel details

### Meeting Tools
- **teams_schedule_meeting** - Schedule Teams meetings
- **teams_list_meetings** - List upcoming meetings
- **teams_get_meeting_info** - Get meeting details
- **teams_join_meeting** - Generate meeting join links

### File and Content Tools
- **teams_upload_file** - Upload files to Teams channels
- **teams_list_files** - List files in channels
- **teams_search_files** - Search for files across Teams

## 🐛 Troubleshooting

### Common Issues

**Authentication Errors:**
```bash
# Check your Azure AD app permissions
# Ensure Microsoft Graph API permissions are granted
```

**Connection Issues:**
```bash
# Test Docker connectivity
docker run --rm -e AZURE_CLIENT_ID="$AZURE_CLIENT_ID" bfljerum/teams-mcp:latest --help
```

### Debug Mode

```bash
# Enable verbose logging
uv run mcp-teams --verbose

# Or with Docker
docker run --rm -p 8000:8000 --env-file .env bfljerum/teams-mcp:latest --verbose
```

## 📋 Requirements

- **Python**: 3.10+ (for local development)
- **Docker**: For containerized deployment
- **UV**: Package manager (for local development)
- **Teams Access**: Valid Azure AD credentials with Teams permissions

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

- **Issues**: [GitHub Issues](https://github.com/sooperset/mcp-teams/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sooperset/mcp-teams/discussions)
- **Documentation**: Check the `.env.example` file for all configuration options

---

**Ready to connect your AI assistant to Microsoft Teams?** Choose your deployment method above and start automating your Teams workflows! 🚀
# 🚀 Slack MCP Server

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-2.12+-green.svg)
![Slack SDK](https://img.shields.io/badge/Slack_SDK-3.27+-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**A powerful [Model Context Protocol (MCP)](https://www.anthropic.com/news/model-context-protocol) server for seamless Slack API integration**

*Connect your AI assistants to Slack with modern Python tooling* ⚡

</div>

---

## ✨ Features

Transform your AI workflow with comprehensive Slack integration:

### 🔧 **Core Tools**
- 📝 **`slack_post_message`** - Send messages to channels
- 💬 **`slack_reply_to_thread`** - Reply to message threads
- 😀 **`slack_add_reaction`** - Add emoji reactions
- 📋 **`slack_list_channels`** - Browse workspace channels with pagination

### 📊 **Data Retrieval**
- 🔍 **`slack_get_channel_history`** - Fetch recent messages from channels
- 🧵 **`slack_get_thread_replies`** - Get complete thread conversations
- 👥 **`slack_get_users`** - Retrieve user profiles and information
- 🔎 **`slack_search_users`** - Search users across all profile fields

### 🔎 **Advanced Search**
- 🔍 **`slack_search_messages`** - Powerful message search with filters (requires user token)
- 📢 **`slack_search_channels`** - Find channels by name

---

## 🏠 Running Locally

### Prerequisites

Before running the Slack MCP Server locally, ensure you have:

- **Python 3.10+** installed
- **UV package manager** installed (`pip install uv`)
- **Slack App** with proper tokens (see [Token Setup](#-how-to-generate-slack-tokens))

### Step-by-Step Local Setup

#### 1. Clone and Navigate

```bash
# Clone the repository
git clone https://github.com/bluefoxlabsai/bfl-mcp-servers.git
cd bfl-mcp-servers/slack-server-mcp
```

#### 2. Install Dependencies

```bash
# Install Python dependencies using UV
uv sync
```

#### 3. Configure Environment

```bash
# Copy the environment template
cp .env.example .env

# Edit .env file with your Slack tokens
# Use your favorite editor (nano, vim, code, etc.)
nano .env
```

Add your tokens to `.env`:

```env
SLACK_BOT_TOKEN=xoxb-your-actual-bot-token-here
SLACK_USER_TOKEN=xoxp-your-actual-user-token-here
SLACK_SAFE_SEARCH=false
```

#### 4. Run the Server

```bash
# Start the MCP server (recommended)
uv run python slack_mcp_server.py --host 0.0.0.0 --port 8000

# Alternative methods
python slack_mcp_server.py --host 0.0.0.0 --port 8000
uv run slack-mcp-server --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### 5. Verify Server is Running

```bash
# Test the health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "server": "SlackMCP",
  "version": "0.1.0"
}
```

#### 6. Test MCP Tools

```bash
# Test available tools endpoint
curl http://localhost:8000/
```

This will show all available MCP tools and server information.

### Alternative: Docker Local Development

If you prefer Docker for local development:

```bash
# Build the image
docker build -t slack-mcp-local .

# Run with your tokens
docker run -p 8000:8000 \
  -e SLACK_BOT_TOKEN=xoxb-your-bot-token \
  -e SLACK_USER_TOKEN=xoxp-your-user-token \
  slack-mcp-local
```

### Connecting to MCP Clients

Once your server is running locally, configure your MCP client:

#### For Claude Desktop (or other MCP clients):

```json
{
  "mcpServers": {
    "slack": {
      "command": "uv",
      "args": ["run", "slack_mcp_server.py"],
      "cwd": "/path/to/bfl-mcp-servers/slack-server-mcp",
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-token",
        "SLACK_USER_TOKEN": "xoxp-your-token"
      }
    }
  }
}
```

#### For HTTP-based MCP clients:

Connect to: `http://localhost:8000`

### Local Development Tips

#### Debug Mode

Enable detailed logging:

```bash
# Set debug environment variable
export SLACK_SDK_DEBUG=true

# Run with debug output
uv run python slack_mcp_server.py --host 0.0.0.0 --port 8000
```

#### Testing Tools Manually

You can test individual tools using curl:

```bash
# List available channels
curl -X POST http://localhost:8000/tools/slack_list_channels \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SLACK_BOT_TOKEN` | Yes | Bot user OAuth token (xoxb-) |
| `SLACK_USER_TOKEN` | Yes | User OAuth token (xoxp-) |
| `SLACK_SAFE_SEARCH` | No | Filter sensitive content (true/false) |
| `SLACK_SDK_DEBUG` | No | Enable debug logging (true/false) |

### Troubleshooting Local Setup

#### Server Won't Start

**Issue**: `ModuleNotFoundError` or dependency errors
**Solution**: Ensure UV installed dependencies:
```bash
uv sync
```

#### Token Authentication Errors

**Issue**: `invalid_auth` when testing tools
**Solution**: 
- Verify tokens start with correct prefixes (`xoxb-` for bot, `xoxp-` for user)
- Check token scopes in Slack app settings
- Ensure app is installed to workspace

#### Port Already in Use

**Issue**: `Port 8000 already in use`
**Solution**: Use a different port by modifying the server code or use a different port:
```bash
# The server currently runs on port 8000 by default
# To change port, modify the main() function in slack_mcp_server.py
```

#### Wrong Server Startup Command

**Issue**: `ERROR: Error loading ASGI app. Attribute "app" not found in module "slack_mcp_server"`
**Solution**: Don't use `uvicorn` directly. Use the correct command:
```bash
# Recommended
uv run python slack_mcp_server.py --host 0.0.0.0 --port 8000

# Alternatives
python slack_mcp_server.py --host 0.0.0.0 --port 8000
uv run slack-mcp-server --host 0.0.0.0 --port 8000
```

#### Permission Errors

**Issue**: `missing_scope` errors
**Solution**: Add required OAuth scopes to your Slack app (see [Token Setup](#-how-to-generate-slack-tokens))

---

## 🚀 Quick Start

### 📦 Installation

<details>
<summary><strong>🌟 Option 1: UV (Recommended)</strong></summary>

```bash
# Clone the repository
git clone https://github.com/bluefoxlabsai/bfl-mcp-servers.git
cd bfl-mcp-servers/slack-server-mcp

# Install dependencies
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your Slack tokens
# SLACK_BOT_TOKEN=xoxb-your-actual-bot-token
# SLACK_USER_TOKEN=xoxp-your-actual-user-token

# Run the server
uv run python slack_mcp_server.py --host 0.0.0.0 --port 8000
```

</details>

<details>
<summary><strong>🐳 Option 2: Docker</strong></summary>

```bash
# Build the image
docker build -t slack-mcp-server .

# Run with your tokens
docker run -p 8000:8000 \
  -e SLACK_BOT_TOKEN=xoxb-your-token \
  -e SLACK_USER_TOKEN=xoxp-your-token \
  slack-mcp-server
```

</details>

---

## 🔑 Required Environment Variables

Create a `.env` file in your project root:

```env
# Required: Slack Bot User OAuth Token
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Required: Slack User OAuth Token (for search features)
SLACK_USER_TOKEN=xoxp-your-user-token-here

# Optional: Enable safe search mode
SLACK_SAFE_SEARCH=false
```

### 🔑 How to Generate Slack Tokens

#### Step 1: Create a Slack App
1. Go to [Slack API](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Enter your app name and select workspace

#### Step 2: Configure Bot Token Scopes
In **"OAuth & Permissions"**:
- Add **Bot Token Scopes**:
  - `channels:read` - View basic information about public channels
  - `channels:history` - View messages and other content in public channels
  - `chat:write` - Send messages as the app
  - `chat:write.public` - Send messages to channels the app is not a member of
  - `groups:read` - View basic information about private channels
  - `groups:history` - View messages in private channels
  - `im:read` - View basic information about direct messages
  - `mpim:read` - View basic information about group direct messages
  - `reactions:write` - Add and edit emoji reactions
  - `users:read` - View people in the workspace
  - `users:read.email` - View email addresses of people in the workspace

#### Step 3: Configure User Token Scopes
In **"OAuth & Permissions"**:
- Add **User Token Scopes**:
  - `search:read` - Search the content and messages in the workspace

#### Step 4: Install App to Workspace
1. Click **"Install to Workspace"** at the top of the OAuth page
2. Review permissions and click **"Allow"**
3. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)
4. Copy the **"User OAuth Token"** (starts with `xoxp-`)

#### Step 5: Add Tokens to Environment
```bash
# Copy the sample environment file
cp .env.example .env

# Edit .env and paste your tokens:
# SLACK_BOT_TOKEN=xoxb-your-actual-bot-token
# SLACK_USER_TOKEN=xoxp-your-actual-user-token
```

---

## 🛠️ MCP Tool Reference

### Core Messaging Tools

#### `slack_post_message`
Send a message to a Slack channel.

**Parameters:**
- `channel_name` (string): Channel name (without #) or channel ID
- `text` (string): Message text to post

**Example:**
```json
{
  "channel_name": "general",
  "text": "Hello from MCP!"
}
```

#### `slack_reply_to_thread`
Reply to a message thread.

**Parameters:**
- `channel_name` (string): Channel name or ID
- `thread_ts` (string): Timestamp of parent message
- `text` (string): Reply text

#### `slack_add_reaction`
Add emoji reaction to a message.

**Parameters:**
- `channel_name` (string): Channel name or ID
- `timestamp` (string): Message timestamp
- `reaction` (string): Emoji name (e.g., "thumbsup", "heart")

### Data Retrieval Tools

#### `slack_list_channels`
List all accessible channels.

**Parameters:**
- `limit` (integer, optional): Max channels to return (default: 100)

#### `slack_get_channel_history`
Get recent messages from a channel.

**Parameters:**
- `channel_name` (string): Channel name or ID
- `limit` (integer, optional): Max messages to return (default: 50)

#### `slack_get_thread_replies`
Get all replies in a thread.

**Parameters:**
- `channel_name` (string): Channel name or ID
- `thread_ts` (string): Parent message timestamp

#### `slack_get_users`
List workspace users.

**Parameters:**
- `limit` (integer, optional): Max users to return (default: 100)

### Search Tools

#### `slack_search_messages`
Search messages (requires user token).

**Parameters:**
- `query` (string): Search query with Slack syntax support
- `limit` (integer, optional): Max results (default: 20)

**Slack Search Syntax:**
- `in:#channel-name` - Search in specific channel
- `from:@username` - Search from specific user
- `before:2024-01-01` - Search before date
- `has:link` - Messages with links
- `has:file` - Messages with files

#### `slack_search_users`
Search users by name or email.

**Parameters:**
- `query` (string): Search term

#### `slack_search_channels`
Search channels by name.

**Parameters:**
- `query` (string): Search term

---

## 🐳 Docker Deployment

### Build & Run

```bash
# Build the image
docker build -t slack-mcp-server .

# Run with environment variables
docker run -p 8000:8000 \
  -e SLACK_BOT_TOKEN=xoxb-your-bot-token \
  -e SLACK_USER_TOKEN=xoxp-your-user-token \
  slack-mcp-server
```

### Docker Compose

```yaml
version: '3.8'
services:
  slack-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SLACK_BOT_TOKEN=xoxb-your-bot-token
      - SLACK_USER_TOKEN=xoxp-your-user-token
    restart: unless-stopped
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

- **Kubernetes cluster** (1.19+)
- **Helm 3** installed
- **kubectl** configured for your cluster
- **Slack tokens** (bot and user tokens)

### Quick Install

```bash
# Navigate to the helm directory
cd helm

# Run the interactive installer
./install.sh
```

The installer will:
- ✅ Create the `mcp-servers` namespace
- ✅ Prompt for your Slack bot and user tokens
- ✅ Create a Kubernetes secret with the tokens
- ✅ Set up image pull authentication for GHCR
- ✅ Install the Helm chart
- ✅ Wait for deployment readiness

### Manual Installation

If you prefer manual installation:

```bash
# 1. Create namespace
kubectl create namespace mcp-servers

# 2. Create secret with Slack tokens
kubectl create secret generic slack-server-mcp-secret \
  --from-literal=bot-token=xoxb-your-bot-token \
  --from-literal=user-token=xoxp-your-user-token \
  -n mcp-servers

# 3. Install Helm chart (image is publicly accessible - no authentication needed)
helm install slack-server-mcp . \
  --namespace mcp-servers \
  --set slack.existingSecret=slack-server-mcp-secret
```

### Post-Installation

```bash
# Check deployment status
kubectl get pods -n mcp-servers

# View logs
kubectl logs -f deployment/slack-server-mcp -n mcp-servers

# Test health endpoint
kubectl port-forward svc/slack-server-mcp 8080:8000 -n mcp-servers
curl http://localhost:8080/health
```

### Configuration

Customize your deployment by creating a `values.yaml` file:

```yaml
# Example values.yaml
replicaCount: 2

image:
  tag: "0.1.0"  # Use specific version instead of latest

slack:
  existingSecret: "my-slack-secret"

# Resource limits
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

Then install with: `helm install slack-server-mcp . -f values.yaml`

---

## 🏗️ Architecture

The Slack MCP Server uses:

- **FastMCP**: Modern MCP server framework
- **Slack SDK**: Official Python SDK for Slack API
- **HTTP Streaming**: Server-sent events on port 8000
- **Environment Variables**: Secure token management
- **Async/Await**: Modern Python async patterns

### Server Flow

1. **Client Connection** → MCP client connects via HTTP streaming
2. **Tool Calls** → Client invokes Slack API tools
3. **Token Validation** → Server validates bot/user tokens
4. **API Calls** → Server makes authenticated Slack API requests
5. **Response Streaming** → Results streamed back to client

---

## 🔒 Security Considerations

- **Token Management**: Store tokens securely, never in code
- **Minimal Permissions**: Use least-privilege token scopes
- **Network Security**: Use HTTPS in production
- **Audit Logging**: Monitor API usage and errors
- **Token Rotation**: Regularly rotate API tokens

### Safe Search Mode

Enable `SLACK_SAFE_SEARCH=true` to filter potentially sensitive content:

```bash
export SLACK_SAFE_SEARCH=true
```

---

## 🐛 Troubleshooting

### Common Issues

#### Token Issues
```
Error: invalid_auth
```
**Solution**: Verify tokens start with correct prefixes:
- Bot token: `xoxb-`
- User token: `xoxp-`

#### Permission Errors
```
Error: missing_scope
```
**Solution**: Add required OAuth scopes to your Slack app

#### Channel Not Found
```
Error: channel_not_found
```
**Solution**: Ensure bot is added to private channels or use channel IDs

### Debug Mode

Enable debug logging:

```bash
export SLACK_SDK_DEBUG=true
uv run python slack_mcp_server.py --host 0.0.0.0 --port 8000
```

---

## 📊 Monitoring & Health Checks

The server provides health check endpoints:

- `GET /health` - Basic health check
- `GET /` - Server info and available tools

### Health Check Response

```json
{
  "status": "healthy",
  "server": "SlackMCP",
  "version": "0.1.0",
  "tools": [
    "slack_post_message",
    "slack_get_channel_history",
    "slack_list_channels",
    ...
  ]
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format .
```

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - Modern MCP server framework
- [Slack SDK](https://github.com/slackapi/python-slack-sdk) - Official Slack Python SDK
- [Model Context Protocol](https://github.com/modelcontextprotocol) - The MCP specification

---

<div align="center">

**Built with ❤️ for the AI assistant community**

[📖 Documentation](https://github.com/bluefoxlabsai/bfl-mcp-servers) •
[🐛 Issues](https://github.com/bluefoxlabsai/bfl-mcp-servers/issues) •
[💬 Discussions](https://github.com/bluefoxlabsai/bfl-mcp-servers/discussions)

</div>
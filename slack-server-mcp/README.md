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
- 📱 **`slack_get_user_profiles`** - Bulk user data operations

### 🔎 **Advanced Search**
- 🔍 **`slack_search_messages`** - Powerful message search with filters:
  - 📍 Location: `in:channel-name`
  - 👤 User: `from:@username` 
  - 📅 Date: `before:2024-01-01`, `after:2023-12-01`
  - 🎯 Content: `has:link`, `has:attachment`, `is:starred`
- 📢 **`slack_search_channels`** - Find channels by name
- 👤 **`slack_search_users`** - Search users across all profile fields

---

## 🚀 Quick Start

### 📦 Installation

<details>
<summary><strong>🌟 Option 1: UV (Recommended)</strong></summary>

```bash
# Install globally
uv add slack-mcp-server

# Or add to existing project
uv add slack-mcp-server --dev
```
</details>

<details>
<summary><strong>🐍 Option 2: Pip</strong></summary>

```bash
pip install slack-mcp-server
```
</details>

<details>
<summary><strong>📥 Option 3: From Source (Development)</strong></summary>

```bash
# Clone the repository
git clone https://github.com/bluefoxlabsai/bfl-mcp-servers.git
cd bfl-mcp-servers/slack-server-mcp

# With uv (recommended)
uv sync

# Or with pip
pip install -e .
```
</details>

---

## 🔧 Configuration

### 🔑 Required Environment Variables

Create a `.env` file in your project root:

```env
# Required: Slack Bot User OAuth Token
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Required: Slack User OAuth Token (for search features)
SLACK_USER_TOKEN=xoxp-your-user-token-here

# Optional: Enable safe search mode
SLACK_SAFE_SEARCH=false
```

### 📋 Token Requirements

| Token | Purpose | Starts with | Required |
|-------|---------|-------------|----------|
| **Bot Token** | Core operations (post, react, etc.) | `xoxb-` | ✅ Yes |
| **User Token** | Search functionality | `xoxp-` | ✅ Yes |

### 🔑 How to Generate Slack Tokens

#### Step 1: Create Slack App
1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Enter app name (e.g., "MCP Server") and select your workspace
4. Click **"Create App"**

#### Step 2: Configure Bot Token Scopes
1. In your app, go to **"OAuth & Permissions"** (left sidebar)
2. Scroll to **"Scopes"** → **"Bot Token Scopes"**
3. Add these scopes:
   - `channels:read` - List public channels
   - `channels:history` - Read message history  
   - `chat:write` - Post messages
   - `reactions:write` - Add emoji reactions
   - `users:read` - Get user information
   - `files:read` - Access file information

#### Step 3: Configure User Token Scopes  
1. In the same **"OAuth & Permissions"** page
2. Scroll to **"User Token Scopes"**
3. Add these scopes:
   - `search:read` - Search messages and files
   - `channels:read` - List channels user has access to
   - `users:read` - Get user information

#### Step 4: Install to Workspace
1. Click **"Install to Workspace"** at the top of the OAuth page
2. Review permissions and click **"Allow"**
3. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)
4. Copy the **"User OAuth Token"** (starts with `xoxp-`)

#### Step 5: Add Tokens to Environment
```bash
# Copy the sample environment file
cp .env.sample .env

# Edit .env and paste your tokens:
# SLACK_BOT_TOKEN=xoxb-your-actual-bot-token
# SLACK_USER_TOKEN=xoxp-your-actual-user-token
```

> **🛡️ Security Note**: Never commit your actual tokens to version control! The `.env` file is in `.gitignore` to prevent accidental commits.

### 🛡️ Safe Search Mode

When `SLACK_SAFE_SEARCH=true`, the server automatically excludes:
- 🔒 Private channels
- 💬 Direct messages  
- 👥 Group messages

---

## 🚀 Running Locally

### 🖥️ Development Setup

```bash
# 1. Clone and navigate
git clone https://github.com/bluefoxlabsai/bfl-mcp-servers.git
cd bfl-mcp-servers/slack-server-mcp

# 2. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv sync

# 4. Set up environment
cp .env.example .env
# Edit .env with your Slack tokens

# 5. Run the server
uv run slack-mcp-server
```

### ⚡ Quick Commands

```bash
# Install dependencies
uv sync

# Run in STDIO mode (default - for AI assistants)
uv run slack-mcp-server

# Run in HTTP mode (for web apps)
uv run slack-mcp-server --port 8000

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code  
uv run ruff check . --fix

# Type checking
uv run mypy slack_mcp_server/
```

---

## 🎯 Usage

### 🔌 Transport Modes

<div align="center">

| Mode | Use Case | Command |
|------|----------|---------|
| **STDIO** 📡 | AI Assistants, Desktop Apps | `uv run slack-mcp-server` |
| **HTTP** 🌐 | Web Apps, APIs, Remote Access | `uv run slack-mcp-server --port 8000` |

</div>

#### 🤖 STDIO Mode (AI Assistants)

```bash
# Global installation
slack-mcp-server

# With uv (from project directory)
uv run slack-mcp-server

# With environment variables
SLACK_BOT_TOKEN=xoxb-xxx SLACK_USER_TOKEN=xoxp-xxx uv run slack-mcp-server
```

#### 🌐 HTTP Mode (Web Applications)

```bash
# Global installation
slack-mcp-server --port 8000

# With uv (from project directory)
uv run slack-mcp-server --port 8000

# Custom port
uv run slack-mcp-server --port 3000
```

### 🐳 Docker

```bash
# Build the image
docker build -t slack-mcp-server .

# Run in STDIO mode
docker run -e SLACK_BOT_TOKEN=xoxb-xxx -e SLACK_USER_TOKEN=xoxp-xxx slack-mcp-server

# Run in HTTP mode
docker run -p 8000:8000 -e SLACK_BOT_TOKEN=xoxb-xxx -e SLACK_USER_TOKEN=xoxp-xxx \
  slack-mcp-server uv run slack-mcp-server --port 8000
```

---

## 📚 Examples

### 🔧 Python Integration
```python
from slack_mcp_server.server import main

# Run in STDIO mode (for AI assistants)
main()

# Run in HTTP mode (for web applications)
main(port=8000)
```

### 📝 Example Scripts

The `examples_python/` directory contains ready-to-use examples:

```bash
# STDIO example - demonstrates process communication
uv run python examples_python/get_users.py

# HTTP example - demonstrates web API integration  
uv run python examples_python/get_users_http.py
```

---

## 🏗️ Architecture

### 🔧 Modern Python Stack

- **🚀 FastMCP**: High-performance MCP framework
- **🔗 Pydantic**: Type-safe data validation and serialization
- **⚡ AsyncIO**: Non-blocking Slack API operations
- **🛠️ UV**: Ultra-fast Python package management
- **🐳 Docker**: Containerized deployment ready

### 🔄 Implementation Pattern

```python
# 1. Schema Definition (Pydantic)
class PostMessageRequest(BaseModel):
    channel: str
    text: str

# 2. Slack API Integration (Async)
async def slack_post_message(request: PostMessageRequest):
    response = await slack_client.chat_postMessage(
        channel=request.channel,
        text=request.text
    )
    return response

# 3. MCP Tool Registration (FastMCP)
@mcp.tool()
async def slack_post_message(request: PostMessageRequest):
    # Implementation with full type safety
    pass
```

---

## 🔧 Development
```

**HTTP Transport**:
```bash
# If installed globally
slack-mcp-server --port 3000

# If using uv from project directory
uv run slack-mcp-server --port 3000
```

### 🛠️ Available Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `uv sync` | Install/update dependencies | `uv sync` |
| `uv run slack-mcp-server` | Run server locally | `uv run slack-mcp-server` |
| `uv run pytest` | Run test suite | `uv run pytest` |
| `uv run black .` | Format code | `uv run black .` |
| `uv run ruff check .` | Lint code | `uv run ruff check . --fix` |
| `uv run mypy slack_mcp_server/` | Type checking | `uv run mypy slack_mcp_server/` |
| `uv add <package>` | Add dependency | `uv add requests` |

### 🔄 Contributing

1. **Fork & Clone**
   ```bash
   git clone https://github.com/yourusername/bfl-mcp-servers.git
   cd bfl-mcp-servers/slack-server-mcp
   ```

2. **Setup Development Environment**
   ```bash
   uv sync
   cp .env.example .env
   # Add your Slack tokens to .env
   ```

3. **Make Changes & Test**
   ```bash
   uv run pytest                    # Run tests
   uv run black .                   # Format code
   uv run ruff check . --fix        # Fix linting
   uv run mypy slack_mcp_server/    # Type check
   ```

4. **Submit PR**
   - Ensure all tests pass
   - Add tests for new features
   - Update documentation

---

## 🎛️ Client Configuration

### 🤖 Claude Desktop (STDIO)

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "slack": {
      "command": "uv",
      "args": ["run", "slack-mcp-server"],
      "cwd": "/path/to/your/project",
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-token",
        "SLACK_USER_TOKEN": "xoxp-your-token"
      }
    }
  }
}
```

### 🌐 HTTP Client Integration

```python
import requests

# Call MCP server via HTTP
response = requests.post(
    "http://localhost:8000/v1/tools/call",
    json={
        "method": "tools/call",
        "params": {
            "name": "slack_post_message",
            "arguments": {
                "channel": "#general",
                "text": "Hello from HTTP!"
            }
        }
    }
)
```

---

## 🎯 Advanced Features

### 🔍 Search Capabilities

**Message Search Examples:**
```bash
# Search in specific channel
"project updates in:dev-team"

# Search by user and date
"from:@john after:2024-01-01 has:link"

# Search with multiple filters  
"bug report from:sarah in:support before:2024-12-01"
```

### 🛡️ Security Features

- **Safe Search Mode**: Automatically excludes private content
- **Token Validation**: Validates Slack tokens on startup
- **Error Handling**: Comprehensive error responses
- **Type Safety**: Full Pydantic validation

---

## 📊 Performance

| Feature | STDIO Mode | HTTP Mode |
|---------|------------|-----------|
| **Latency** | ~50ms | ~100ms |
| **Throughput** | Single client | Multiple clients |
| **Memory** | Process-based | Always running |
| **Network** | Local only | Network accessible |

---

## 🤝 Support

- 📝 **Issues**: [GitHub Issues](https://github.com/bluefoxlabsai/bfl-mcp-servers/issues)
- 📧 **Email**: support@bluefoxlabs.ai  
- 🌐 **Website**: [Blue Fox Labs](https://bluefoxlabs.ai)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by [Blue Fox Labs AI](https://bluefoxlabs.ai)**

*Empowering AI with seamless integrations*

</div>
{
  "slack": {
    "command": "slack-mcp-server",
    "env": {
      "SLACK_BOT_TOKEN": "<your-bot-token>",
      "SLACK_USER_TOKEN": "<your-user-token>",
      "SLACK_SAFE_SEARCH": "false"
    }
  }
}
```

**For HTTP Transport (Web applications)**:

Start the server:
```bash
SLACK_BOT_TOKEN=<your-bot-token> SLACK_USER_TOKEN=<your-user-token> slack-mcp-server --port 3000
```

Connect to: `http://localhost:3000/mcp`

### Examples

#### Python Examples

See [examples_python/README.md](examples_python/README.md) for detailed Python client examples:

- **STDIO Example**: `examples_python/get_users.py` - Demonstrates STDIO transport
- **HTTP Example**: `examples_python/get_users_http.py` - Demonstrates HTTP transport

Run the examples:
```bash
# STDIO example
python examples_python/get_users.py

# Or with uv from project directory
uv run python examples_python/get_users.py

# HTTP example  
python examples_python/get_users_http.py

# Or with uv from project directory
uv run python examples_python/get_users_http.py
```

#### TypeScript Examples (Legacy)

The original TypeScript examples are still available in the `examples/` directory for reference.

## Implementation Pattern

This server follows modern Python development practices:

1. **Schema Definition**: Using Pydantic models for request/response validation
   - Request schemas: Define input parameters with validation
   - Response schemas: Define structured responses with type safety

2. **Implementation flow**:
   - Validate request with Zod schema
   - Call Slack WebAPI
   - Parse response with Zod schema to limit to necessary fields
   - Return as JSON

For example, the `slack_list_channels` implementation parses the request with `ListChannelsRequestSchema`, calls `slackClient.conversations.list`, and returns the response parsed with `ListChannelsResponseSchema`.

## Development

### Available Commands

- `uv run pytest` - Run tests
- `uv run black .` - Format code with Black
- `uv run ruff check .` - Run linting checks with Ruff
- `uv run ruff check . --fix` - Auto-fix linting issues
- `uv run mypy slack_mcp_server/` - Run type checking with MyPy
- `uv sync` - Install/update dependencies
- `uv add <package>` - Add a new dependency
- `uv run slack-mcp-server` - Run the server locally

### Development Setup

```bash
# Clone and set up the project
git clone https://github.com/bluefoxlabsai/bfl-mcp-servers.git
cd bfl-mcp-servers/slack-server-mcp

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your Slack tokens

# Run the server
uv run slack-mcp-server
```
- `npm run fix` - Automatically fix linting issues

### Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests and linting: `npm run lint`
4. Commit your changes
5. Push to the branch
6. Create a Pull Request

# 🔍 Google Search MCP Server

<div align="center">

[![smithery badge](https://smithery.ai/badge/@gradusnikov/google-search-mcp-server)](https://smithery.ai/server/@gradusnikov/google-search-mcp-server)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-compatible-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**🤖 A powerful [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that enables AI assistants like Claude to perform Google searches**

</div>

---

## ✨ Features

🔍 **Search Tool** - Perform Google searches with customizable result limits  
📊 **Structured Results** - Returns formatted search results with titles, links, and snippets  
⚡ **Error Handling** - Graceful handling of API errors and rate limits  
🚀 **Fast Performance** - Built with FastMCP for optimal speed  
🔌 **Easy Integration** - Compatible with Claude Desktop and other MCP clients

## 📋 Prerequisites

| Requirement | Description |
|-------------|-------------|
| 🔑 **Google Cloud API Key** | Google Cloud project with Custom Search API enabled |
| 🔍 **Custom Search Engine ID** | CSE created through Google's CSE console |
| 🐍 **Python 3.10+** | Required for FastMCP compatibility |

## 📦 Installation

### 🎯 Option 1: Via Smithery (Recommended)

Install automatically for Claude Desktop:

```bash
npx -y @smithery/cli install @gradusnikov/google-search-mcp-server --client claude
```

### 🛠️ Option 2: Manual Installation

#### 1. 📥 **Clone the repository**:
```bash
git clone https://github.com/hubbertj/google-search-mcp-server.git
cd google-search-mcp-server
```

#### 2. 🚀 **Install uv** (if not already installed):
```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

#### 3. 📚 **Install dependencies**:
```bash
uv sync
```

## ⚙️ Configuration

### 🔐 1. Get Google API Credentials

#### 🌐 **Create a Google Cloud Project**:
- Go to the [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project or select an existing one

#### 🔧 **Enable the Custom Search API**:
- Navigate to "APIs & Services" > "Library"
- Search for "Custom Search API" and enable it

#### 🗝️ **Create an API Key**:
- Go to "APIs & Services" > "Credentials"
- Click "Create Credentials" > "API Key"
- Copy your API key

#### 🔍 **Create a Custom Search Engine**:
- Visit [Google Custom Search Engine](https://cse.google.com/cse/all)
- Click "Add" to create a new search engine
- Configure your search preferences
- Copy the Search Engine ID

### 📝 2. Environment Configuration

Copy the example environment file and configure it with your credentials:

```bash
cp .env.example .env
```

Then edit the `.env` file with your actual values:

```bash
# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
```

## 🚀 Usage

### ▶️ Running the Server

Start the MCP server:

```bash
uv run google_search_mcp_server.py
```

### 🤖 Claude Desktop Integration

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "google-search": {
      "command": "uv",
      "args": ["run", "/path/to/google-search-mcp-server/google_search_mcp_server.py"],
      "env": {
        "GOOGLE_API_KEY": "your_google_api_key_here",
        "GOOGLE_CSE_ID": "your_custom_search_engine_id_here"
      }
    }
  }
}
```

### 🔌 Using with Other MCP Clients

The server exposes a `search_google` tool that accepts:
- 📝 `query` (string): The search query
- 🔢 `num_results` (integer, optional): Number of results to return (default: 5)

**Example response:**
```json
{
  "success": true,
  "results": [
    {
      "title": "Example Result Title",
      "link": "https://example.com",
      "snippet": "A brief description of the search result..."
    }
  ],
  "total_results": "1000000"
}
```

### ☸️ Kubernetes Deployment with Helm

Deploy to Kubernetes using the included Helm chart:

#### **Prerequisites**
- Kubernetes cluster (1.19+)
- Helm 3.x installed
- kubectl configured

#### **Quick Deploy**
```bash
# Clone the repository
git clone https://github.com/hubbertj/google-search-mcp-server.git
cd google-search-mcp-server

# Install with Helm
helm install google-search-mcp ./helm/google-search-mcp-server \
  --set googleApi.apiKey="your_google_api_key_here" \
  --set googleApi.cseId="your_google_cse_id_here"
```

#### **Production Deployment**
```bash
# Copy and customize the production values
cp helm/google-search-mcp-server/values-production.yaml my-values.yaml
# Edit my-values.yaml with your configuration

# Deploy with production settings
helm install google-search-mcp ./helm/google-search-mcp-server -f my-values.yaml
```

#### **Configuration Options**
| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `google-search-mcp-server` |
| `image.tag` | Container image tag | `Chart.appVersion` |
| `googleApi.apiKey` | Google API Key | `""` |
| `googleApi.cseId` | Google Custom Search Engine ID | `""` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8080` |
| `ingress.enabled` | Enable ingress | `false` |
| `autoscaling.enabled` | Enable HPA | `false` |
| `resources.limits.cpu` | CPU limit | `unset` |
| `resources.limits.memory` | Memory limit | `unset` |

#### **Helm Commands**
```bash
# Check deployment status
helm status google-search-mcp

# Upgrade deployment
helm upgrade google-search-mcp ./helm/google-search-mcp-server \
  --set googleApi.apiKey="new_api_key"

# Uninstall
helm uninstall google-search-mcp

# View generated manifests
helm template google-search-mcp ./helm/google-search-mcp-server
```

## 🛠️ Development

### 📁 Project Structure

```
google-search-mcp-server/
├── 🐍 google_search_mcp_server.py  # Main server implementation
├── 📦 pyproject.toml               # Project configuration
├── 🔒 uv.lock                      # Dependency lock file
├── 🔧 .env                         # Environment variables (create this)
├── 🐳 Dockerfile                   # Container configuration
├── ⎈ helm/                         # Helm chart for Kubernetes deployment
│   └── google-search-mcp-server/
│       ├── Chart.yaml              # Helm chart metadata
│       ├── values.yaml             # Default configuration values
│       ├── values-production.yaml  # Production configuration
│       └── templates/              # Kubernetes manifest templates
└── 📖 README.md                    # This file
```

### 🧪 Running Tests

```bash
# Test the search functionality
uv run python -c "
import asyncio
from google_search_mcp_server import search_google
result = asyncio.run(search_google('Python programming', 3))
print(result)
"
```

### 🐳 Building Docker Image

```bash
docker build -t google-search-mcp-server .
docker run -e GOOGLE_API_KEY=your_key -e GOOGLE_CSE_ID=your_id google-search-mcp-server
```

## 🔧 Troubleshooting

### ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| 🔑 **API Key Issues** | Ensure your Google Cloud project has the Custom Search API enabled |
| 🚦 **Rate Limits** | Google Custom Search has daily query limits |
| 🔍 **Search Engine Configuration** | Make sure your CSE is configured to search the web |
| 📁 **Environment Variables** | Verify your `.env` file is in the project root |

### 🚨 Error Messages

- `API Error: ...` → Check your Google API key and CSE ID
- `HTTP 429` → You've exceeded your daily search quota  
- `Module not found` → Run `uv sync` to install dependencies

---

## 📄 License

This project is open source. Please check the repository for license details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

<div align="center">

**Made with ❤️ for the MCP community**

</div>

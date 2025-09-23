# 🔍 Google Search MCP Server

<div align="center">

[![smithery badge](https://smithery.ai/badge/@gradusnikov/google-search-mcp-server)](https://smithery.ai/server/@gradusnikov/google-search-mcp-server)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-compatible-green.svg)
![Docker](https://img.shields.io/badge/docker-available-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**🤖 A powerful [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that enables AI assistants like Claude to perform Google searches**

Available as: **📦 Python Package** | **🐳 Docker Image** | **☸️ Helm Chart**

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

### ▶️ Running the Basic Server

Start the basic MCP server:

```bash
uv run google_search_mcp_server.py
```

### 🚀 Running the Enhanced Server (Recommended)

The enhanced server provides comprehensive Google Search functionality with 9 advanced search tools:

#### **Local Development**

```bash
# Run with default settings (SSE transport on localhost:8000)
uv run python enhanced_google_search_server.py

# Run with custom host and port
uv run python enhanced_google_search_server.py --host 0.0.0.0 --port 8000

# Run with different transport protocols
uv run python enhanced_google_search_server.py --transport sse          # Server-Sent Events (default)
uv run python enhanced_google_search_server.py --transport streamable-http  # HTTP transport
uv run python enhanced_google_search_server.py --transport stdio       # Standard I/O (for MCP clients)
```

#### **Enhanced Features**

The enhanced server includes these advanced search tools:

🔍 **`search_google`** - Comprehensive search with pagination, language, and country options  
🖼️ **`search_images`** - Image search with size, type, and safety filters  
📅 **`search_by_date_range`** - Search with date filtering and sorting  
🌐 **`search_site_specific`** - Search within or exclude specific websites  
📄 **`search_file_type`** - Search for specific file types (PDF, DOC, etc.)  
🔗 **`search_related`** - Find pages related to a specific URL  
💾 **`search_cached`** - Get cached versions of web pages  
💡 **`get_search_suggestions`** - Get search suggestions for queries  
🔍 **`get_api_status`** - Check API configuration and quota status

#### **Enhanced Server Options**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--host` | Host to bind the server to | `127.0.0.1` |
| `--port` | Port to bind the server to | `8000` |
| `--transport` | Transport protocol | `sse` |

**Available transports:**
- `sse` - Server-Sent Events (recommended for web clients)
- `streamable-http` - HTTP transport (for LibreChat integration)
- `stdio` - Standard I/O (for traditional MCP clients)

### 🤖 Claude Desktop Integration

#### **Basic Server Integration**

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

#### **Enhanced Server Integration (Recommended)**

For the enhanced server with comprehensive search functionality:

```json
{
  "mcpServers": {
    "google-search-enhanced": {
      "command": "uv",
      "args": ["run", "/path/to/google-search-mcp-server/enhanced_google_search_server.py", "--transport", "stdio"],
      "env": {
        "GOOGLE_API_KEY": "your_google_api_key_here",
        "GOOGLE_CSE_ID": "your_custom_search_engine_id_here"
      }
    }
  }
}
```

#### **HTTP Server Integration (LibreChat/Web)**

For web-based integrations using HTTP transport:

```json
{
  "mcpServers": {
    "google-search-http": {
      "type": "streamable-http",
      "url": "http://localhost:8000",
      "timeout": 30000
    }
  }
}
```

**Start the HTTP server:**
```bash
uv run python enhanced_google_search_server.py --host 0.0.0.0 --port 8000 --transport streamable-http
```

### 🔌 Using with Other MCP Clients

#### **Basic Server Tools**

The basic server exposes a `search_google` tool that accepts:
- 📝 `query` (string): The search query
- 🔢 `num_results` (integer, optional): Number of results to return (default: 5)

#### **Enhanced Server Tools**

The enhanced server provides comprehensive search functionality:

**🔍 search_google** - Advanced web search
- `query` (string): Search query
- `num_results` (int): Results count (1-10, default: 10)
- `start_index` (int): Pagination start (default: 1)
- `language` (string): Language code (default: "en")
- `country` (string): Country code (default: "us")

**🖼️ search_images** - Image search
- `query` (string): Image search query
- `num_results` (int): Results count (1-10, default: 10)
- `image_size` (string): Size filter (huge, icon, large, medium, small, xlarge, xxlarge)
- `image_type` (string): Type filter (clipart, face, lineart, stock, photo, animated)
- `safe_search` (string): Safety setting (active, off)

**📅 search_by_date_range** - Date-filtered search
- `query` (string): Search query
- `start_date` (string): Start date (YYYY-MM-DD)
- `end_date` (string): End date (YYYY-MM-DD)
- `num_results` (int): Results count (1-10, default: 10)
- `sort_by` (string): Sort order (date, relevance)

**🌐 search_site_specific** - Site-restricted search
- `query` (string): Search query
- `site` (string): Target site (e.g., "reddit.com")
- `num_results` (int): Results count (1-10, default: 10)
- `exclude_sites` (array): Sites to exclude

**📄 search_file_type** - File type search
- `query` (string): Search query
- `file_type` (string): File type (pdf, doc, xls, ppt, etc.)
- `num_results` (int): Results count (1-10, default: 10)
- `exact_terms` (string): Exact phrase to include
- `exclude_terms` (string): Terms to exclude

**🔗 search_related** - Related pages
- `url` (string): URL to find related pages for
- `num_results` (int): Results count (1-10, default: 10)

**💾 search_cached** - Cached pages
- `url` (string): URL to get cached version for

**💡 get_search_suggestions** - Search suggestions
- `query` (string): Query to get suggestions for
- `max_suggestions` (int): Maximum suggestions to return

**🔍 get_api_status** - API status check
- No parameters required

**Example response:**
```json
{
  "success": true,
  "results": [
    {
      "title": "Example Result Title",
      "link": "https://example.com",
      "snippet": "A brief description of the search result...",
      "display_link": "example.com",
      "formatted_url": "https://example.com/page",
      "meta_description": "Meta description if available",
      "meta_image": "https://example.com/image.jpg"
    }
  ],
  "total_results": "1000000",
  "search_time": 0.123,
  "formatted_total_results": "About 1,000,000 results",
  "formatted_search_time": "0.12 seconds"
}
```
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
helm install google-search-mcp ./helm \
  --set googleApi.apiKey="your_google_api_key_here" \
  --set googleApi.cseId="your_google_cse_id_here"
```

#### **Production Deployment**
```bash
# Copy and customize the production values
cp helm/values-production.yaml my-values.yaml
# Edit my-values.yaml with your configuration

# Deploy with production settings
helm install google-search-mcp ./helm -f my-values.yaml
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
helm upgrade google-search-mcp ./helm \
  --set googleApi.apiKey="new_api_key"

# Uninstall
helm uninstall google-search-mcp

# View generated manifests
helm template google-search-mcp ./helm
```

## 🛠️ Development

### 📁 Project Structure

```
google-search-mcp-server/
├── 🐍 google_search_mcp_server.py     # Basic server implementation
├── 🚀 enhanced_google_search_server.py # Enhanced server with 9 advanced tools
├── 📦 pyproject.toml                   # Project configuration
├── 🔒 uv.lock                          # Dependency lock file
├── 🔧 .env                             # Environment variables (create this)
├── 🐳 Dockerfile                       # Container configuration
├── 🐳 Dockerfile.enhanced              # Enhanced server container
├── 📋 Makefile                         # Build and deployment commands
├── ⎈ helm/                             # Helm chart for Kubernetes deployment
│       ├── Chart.yaml                  # Helm chart metadata
│       ├── values.yaml                 # Default configuration values
│       ├── values-production.yaml      # Production configuration
│       └── templates/                  # Kubernetes manifest templates
└── 📖 README.md                        # This file
```

### 🧪 Running Tests

#### **Test Basic Server**
```bash
# Test the basic search functionality
uv run python -c "
import asyncio
from google_search_mcp_server import search_google
result = asyncio.run(search_google('Python programming', 3))
print(result)
"
```

#### **Test Enhanced Server**
```bash
# Test enhanced server functionality
uv run python -c "
import asyncio
from enhanced_google_search_server import search_google, search_images, get_api_status

async def test_enhanced():
    # Test basic search
    result = await search_google('FastMCP framework', 3)
    print('Basic search:', result)
    
    # Test image search
    images = await search_images('python logo', 2)
    print('Image search:', images)
    
    # Test API status
    status = await get_api_status()
    print('API status:', status)

asyncio.run(test_enhanced())
"
```

#### **Test Enhanced Server HTTP Mode**
```bash
# Start the server in background
uv run python enhanced_google_search_server.py --host 127.0.0.1 --port 8000 &

# Test with curl (in another terminal)
curl -X POST http://127.0.0.1:8000/message \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "search_google",
      "arguments": {
        "query": "FastMCP python framework",
        "num_results": 3
      }
    }
  }'
```

### 🐳 Building Docker Images

#### **Basic Server**
```bash
docker build -t google-search-mcp-server .
docker run -e GOOGLE_API_KEY=your_key -e GOOGLE_CSE_ID=your_id google-search-mcp-server
```

#### **Enhanced Server** (Recommended)
```bash
# Pull pre-built image from Docker Hub
docker pull bfljerum/google-search-mcp:latest

# Or build locally
docker build -f Dockerfile.enhanced -t bfljerum/google-search-mcp:latest .

# Run with SSE transport (web accessible)
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e GOOGLE_CSE_ID=your_id \
  bfljerum/google-search-mcp:latest

# Run with streamable-http transport (LibreChat compatible)
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e GOOGLE_CSE_ID=your_id \
  bfljerum/google-search-mcp:latest \
  python enhanced_google_search_server.py --transport streamable-http --host 0.0.0.0 --port 8000

# Access the running server
curl http://localhost:8000
```

#### **Using Makefile**
```bash
# Build and run enhanced server
make docker-build-enhanced
make docker-run-enhanced GOOGLE_API_KEY=your_key GOOGLE_CSE_ID=your_id

# Build both servers
make docker-build-all
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

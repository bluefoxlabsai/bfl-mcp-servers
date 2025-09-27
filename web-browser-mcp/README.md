# MCP Web Browser

![License](https://img.shields.io/github/license/bluefoxlabsai/bfl-mcp-servers)

**Model Context Protocol (MCP) server for web browsing** - Enable AI assistants to browse the web and extract content from websites using headless browser technology.

## ✨ Features

- **🌐 Web Content Extraction** - "Browse to example.com and get the main content"
- **📄 Page Title Retrieval** - "Get the title of https://github.com"
- **🔍 Headless Browser** - Uses Chromium for reliable web scraping
- **🚀 Streamable HTTP** - Supports MCP's streamable HTTP transport on port 8000

## 📦 Available Deployment Options

- **🐳 Docker Image**: Build from source
- **🐍 Python Package**: Install with UV
- **☸️ Kubernetes**: Helm chart in `/helm` directory
- **💻 Local Development**: Clone and run with UV

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** with **UV**
- **Docker** (optional, for containerized deployment)

### 1. Install with UV

```bash
# Clone the repository
git clone https://github.com/bluefoxlabsai/bfl-mcp-servers.git
cd bfl-mcp-servers/web-browser-mcp

# Install dependencies
uv sync

# Run the server
uv run mcp-web-browser --transport streamable-http --port 8000
```

### 2. Using Docker

```bash
# Build the image
docker build -t mcp-web-browser .

# Run the container
docker run -p 8000:8000 mcp-web-browser
```

### 3. Using Kubernetes (Helm)

```bash
# Install the Helm chart
cd helm
./install.sh
```

## 🔧 Configuration

The server supports the following transport modes:

- **stdio**: Standard input/output (default)
- **sse**: Server-Sent Events
- **streamable-http**: Streamable HTTP (recommended for web)

### Environment Variables

- `PORT`: Port for HTTP transports (default: 8000)
- `HOST`: Host to bind to (default: 0.0.0.0)

## 🛠️ Available Tools

### `browse_url`

Browse to a URL and extract the text content of the page.

**Parameters:**
- `url` (string): The URL to browse to
- `wait_for_selector` (string, optional): CSS selector to wait for before extracting content

**Example:**
```json
{
  "url": "https://example.com",
  "wait_for_selector": ".main-content"
}
```

### `get_page_title`

Get the title of a web page.

**Parameters:**
- `url` (string): The URL to get the title from

**Example:**
```json
{
  "url": "https://github.com"
}
```

## 🧪 Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=mcp_web_browser
```

## 📝 Development

```bash
# Install development dependencies
uv sync --dev

# Run linting
uv run ruff check

# Format code
uv run black .
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
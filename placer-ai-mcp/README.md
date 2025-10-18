# MCP Placer.ai

[![Docker Pulls](https://img.shields.io/docker/pulls/bluefoxlabsai/placer-ai-mcp)](https://hub.docker.com/r/bluefoxlabsai/placer-ai-mcp)
![License](https://img.shields.io/github/license/bluefoxlabsai/placer-ai-mcp)

**Model Context Protocol (MCP) server for Placer.ai Location Analytics** - Connect AI assistants to Placer.ai's comprehensive location intelligence platform for foot traffic analysis, demographics insights, and competitor analysis.

## ✨ Features

- **🏢 Location Discovery** - "Find retail locations in downtown San Francisco"
- **📊 Foot Traffic Analysis** - "Show me visit patterns for Starbucks locations in NYC"
- **👥 Demographics Insights** - "What are the demographics of Target shoppers?"
- **🏆 Competitor Analysis** - "Compare foot traffic between McDonald's and Burger King"
- **📍 Trade Area Analysis** - "Analyze the trade area for this shopping mall"

### Placer.ai Data Coverage

| Data Type           | Coverage                    |
|--------------------|-----------------------------|
| **Locations**      | 1M+ POIs globally          |
| **Foot Traffic**   | Real-time & historical     |
| **Demographics**   | Age, income, interests      |
| **Trade Areas**    | Customizable radii         |
| **Competitors**    | Cross-brand analysis       |

## 📦 Available Deployment Options

[![Docker Hub](https://img.shields.io/docker/v/bluefoxlabsai/placer-ai-mcp?label=Docker%20Hub&style=for-the-badge&logo=docker)](https://hub.docker.com/r/bluefoxlabsai/placer-ai-mcp)

- **🐳 Docker Image**: `ghcr.io/bluefoxlabsai/placer-ai-mcp:latest` (Multi-platform: AMD64, ARM64)
- **🐍 Python Package**: `uv add mcp-placer-ai` 
- **☸️ Kubernetes**: Production-ready Helm chart with interactive installer in `/helm` directory
- **💻 Local Development**: Clone and run with UV

## 🚀 Quick Start

### Prerequisites

- **Placer.ai Account**: Get your API key from [Placer.ai](https://www.placer.ai/)
- **Docker** or **Python 3.10+** with **UV**

### 1. Get Your API Credentials

1. Sign up at [Placer.ai](https://www.placer.ai/)
2. Navigate to your API settings
3. Generate an API key
4. Copy the key immediately

### 2. Choose Your Deployment Method

## 🐳 Docker Deployment

### Run with Docker

```bash
# Pull the official image from GitHub Container Registry
docker pull ghcr.io/bluefoxlabsai/placer-ai-mcp:latest

# Run with your API key
docker run --rm -p 8000:8000 \
  -e PLACER_AI_API_KEY="your_placer_ai_api_key" \
  ghcr.io/bluefoxlabsai/placer-ai-mcp:latest

# Or use environment file
docker run --rm -p 8000:8000 --env-file .env \
  ghcr.io/bluefoxlabsai/placer-ai-mcp:latest
```

### Environment File (.env)

```bash
# Required
PLACER_AI_API_KEY=your_placer_ai_api_key

# Optional Configuration
PLACER_AI_BASE_URL=https://api.placer.ai/v1
PLACER_AI_TIMEOUT=30
PLACER_AI_CACHE_TTL=300
PLACER_AI_CACHE_MAX_SIZE=1000
```

## ☸️ Kubernetes Deployment

### Interactive Helm Installation

```bash
# Clone the repository
git clone https://github.com/bluefoxlabsai/placer-ai-mcp.git
cd placer-ai-mcp/helm

# Run interactive installer
./install.sh

# Or install with your API key
PLACER_AI_API_KEY=your_key ./install.sh
```

### Manual Helm Installation

```bash
# Add the repository
helm repo add bluefoxlabsai https://charts.bluefoxlabsai.com
helm repo update

# Install with your API key
helm install placer-ai-mcp bluefoxlabsai/placer-ai-mcp \
  --namespace mcp-servers --create-namespace \
  --set placerAI.apiKey=your_placer_ai_api_key
```

## 🐍 Python Development

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/bluefoxlabsai/placer-ai-mcp.git
cd placer-ai-mcp

# Install dependencies with UV
uv sync

# Set environment variables
export PLACER_AI_API_KEY=your_placer_ai_api_key

# Run the server
uv run mcp-placer-ai --transport streamable-http --host 0.0.0.0 --port 8000
```

### Install as Package

```bash
# Install from PyPI (when published)
pip install mcp-placer-ai

# Or install from source
uv add git+https://github.com/bluefoxlabsai/placer-ai-mcp.git
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PLACER_AI_API_KEY` | ✅ | - | Your Placer.ai API key |
| `PLACER_AI_BASE_URL` | ❌ | `https://api.placer.ai/v1` | API base URL |
| `PLACER_AI_TIMEOUT` | ❌ | `30` | Request timeout (seconds) |
| `PLACER_AI_CACHE_TTL` | ❌ | `300` | Cache TTL (seconds) |
| `PLACER_AI_CACHE_MAX_SIZE` | ❌ | `1000` | Max cache entries |

### MCP Transport Options

| Transport | URL | Use Case |
|-----------|-----|----------|
| `stdio` | - | Direct process communication |
| `streamable-http` | `http://localhost:8000` | HTTP-based MCP (recommended) |
| `sse` | `http://localhost:8000` | Server-sent events |

## 📚 Available Tools

The Placer.ai MCP server provides these tools for AI assistants:

### 🔍 search_locations
Search for locations and points of interest.

**Parameters:**
- `query` (string): Search query (e.g., "Starbucks", "shopping malls")
- `location` (optional): Location filter (e.g., "New York, NY")
- `limit` (optional): Number of results (default: 10)

**Example:**
```json
{
  "query": "coffee shops",
  "location": "San Francisco, CA",
  "limit": 5
}
```

### 📊 get_visits_analysis
Analyze foot traffic patterns for locations.

**Parameters:**
- `location_id` (string): Placer.ai location ID
- `start_date` (string): Start date (YYYY-MM-DD)
- `end_date` (string): End date (YYYY-MM-DD)
- `metrics` (optional): Specific metrics to analyze

**Example:**
```json
{
  "location_id": "loc_12345",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

### 🏆 get_competitor_analysis
Compare performance between locations or brands.

**Parameters:**
- `primary_location_id` (string): Primary location ID
- `competitor_location_ids` (array): Array of competitor location IDs
- `start_date` (string): Analysis start date
- `end_date` (string): Analysis end date

**Example:**
```json
{
  "primary_location_id": "loc_12345",
  "competitor_location_ids": ["loc_67890", "loc_54321"],
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

### 👥 get_demographics_analysis
Get demographic insights for location visitors.

**Parameters:**
- `location_id` (string): Location ID to analyze
- `start_date` (string): Analysis start date
- `end_date` (string): Analysis end date
- `demographic_types` (optional): Specific demographics to analyze

**Example:**
```json
{
  "location_id": "loc_12345",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "demographic_types": ["age", "income", "interests"]
}
```

### 📍 get_trade_area_analysis
Analyze trade area characteristics and patterns.

**Parameters:**
- `location_id` (string): Location ID for trade area
- `radius_miles` (optional): Analysis radius in miles (default: 3)
- `start_date` (string): Analysis start date
- `end_date` (string): Analysis end date

**Example:**
```json
{
  "location_id": "loc_12345",
  "radius_miles": 5,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

## 🔌 Connecting to MCP Clients

### Claude Desktop (Anthropic)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "placer-ai": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "PLACER_AI_API_KEY=your_placer_ai_api_key",
        "ghcr.io/bluefoxlabsai/placer-ai-mcp:latest"
      ]
    }
  }
}
```

### Cline VS Code Extension

Add to your MCP settings:

```json
{
  "placer-ai": {
    "command": "uv",
    "args": ["run", "mcp-placer-ai"],
    "env": {
      "PLACER_AI_API_KEY": "your_placer_ai_api_key"
    }
  }
}
```

### HTTP-based Connection

For streamable-http transport:

```bash
# Start the server
docker run -p 8000:8000 \
  -e PLACER_AI_API_KEY=your_api_key \
  ghcr.io/bluefoxlabsai/placer-ai-mcp:latest

# Connect via HTTP
curl http://localhost:8000/health
```

## 🏥 Health Checks

The server provides health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/status
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime": "PT1H30M",
  "placer_ai_api": "connected"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Invalid**
   ```
   Error: 401 Unauthorized
   Solution: Verify your API key is correct and active
   ```

2. **Connection Timeout**
   ```
   Error: Request timeout
   Solution: Check network connectivity and increase timeout
   ```

3. **Rate Limiting**
   ```
   Error: 429 Too Many Requests
   Solution: Reduce request frequency or upgrade plan
   ```

### Debug Mode

Enable verbose logging:

```bash
# Docker
docker run -e MCP_VERBOSE=true ghcr.io/bluefoxlabsai/placer-ai-mcp:latest

# Python
uv run mcp-placer-ai --verbose
```

### Support

- 📧 **Email**: support@bluefoxlabsai.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/bluefoxlabsai/placer-ai-mcp/issues)
- 📖 **Documentation**: [Official Docs](https://docs.bluefoxlabsai.com/mcp/placer-ai)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/bluefoxlabsai/placer-ai-mcp.git
cd placer-ai-mcp
uv sync

# Run tests
uv run pytest

# Format code
uv run ruff check
uv run ruff format
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [MCP AccuWeather](../accuweather-mcp/) - Weather data integration
- [MCP Atlassian](../atlassian-mcp/) - Jira and Confluence integration
- [MCP Google Search](../google-search-mcp/) - Google Search integration
- [MCP Nasdaq](../nasdaq-data-link-mcp/) - Financial data integration

---

**Built with ❤️ by [BlueFox Labs AI](https://bluefoxlabsai.com)**
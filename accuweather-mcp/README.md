# 🌤️ AccuWeather MCP Server

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-2.3+-green.svg)
![AccuWeather](https://img.shields.io/badge/AccuWeather-API-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**A powerful [Model Context Protocol (MCP)](https://www.anthropic.com/news/model-context-protocol) server for AccuWeather API integration**

*Connect your AI assistants to real-time weather data* ⚡

</div>

---

## ✨ Features

Transform your AI workflow with comprehensive weather data integration:

### 🔧 **Core Tools**
- 🔍 **`search_locations`** - Find locations by name, postal code, or coordinates
- 🌡️ **`get_current_weather`** - Get real-time weather conditions
- 📅 **`get_daily_forecast`** - Multi-day weather forecasts (1-15 days)
- ⏰ **`get_hourly_forecast`** - Detailed hourly forecasts (1-120 hours)

### 🚨 **Advanced Features**
- ⚠️ **`get_weather_alerts`** - Active weather warnings and advisories
- 📍 **`get_location_by_coordinates`** - Reverse geocoding for lat/lon
- 📊 **`get_historical_weather`** - Historical weather data

### 🎯 **Key Capabilities**
- **Real-time Data**: Current conditions with detailed metrics
- **Comprehensive Forecasts**: Temperature, precipitation, wind, humidity
- **Weather Alerts**: Severe weather warnings and watches
- **Global Coverage**: Worldwide location support
- **Caching**: Built-in response caching for performance
- **Rate Limiting**: Automatic API rate limit handling

---

## 🚀 Quick Start

### 📦 Installation

<details>
<summary><strong>🌟 Option 1: UV (Recommended)</strong></summary>

```bash
# Install globally
uv add mcp-accuweather

# Or add to existing project
uv add mcp-accuweather --dev
```
</details>

<details>
<summary><strong>🐍 Option 2: Pip</strong></summary>

```bash
pip install mcp-accuweather
```
</details>

<details>
<summary><strong>📥 Option 3: From Source (Development)</strong></summary>

```bash
# Clone the repository
git clone https://github.com/bluefoxlabsai/bfl-mcp-servers.git
cd bfl-mcp-servers/accuweather-mcp

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
# Required: AccuWeather API Key
ACCUWEATHER_API_KEY=your-api-key-here

# Optional: API Base URL (default: http://dataservice.accuweather.com)
ACCUWEATHER_BASE_URL=http://dataservice.accuweather.com

# Optional: Cache configuration
CACHE_TTL=300
CACHE_MAXSIZE=1000

# Optional: Request timeout
REQUEST_TIMEOUT=30
```

### 🔑 How to Get AccuWeather API Key

1. **Create Account**: Go to [AccuWeather Developer Portal](https://developer.accuweather.com/)
2. **Register**: Sign up for a free developer account
3. **Create App**: Create a new application in your dashboard
4. **Get API Key**: Copy your API key from the app details
5. **Choose Plan**: 
   - **Limited Trial**: 50 calls/day (free)
   - **Core Weather**: 1,000 calls/day
   - **Standard**: 5,000 calls/day
   - **Premium**: Unlimited calls

> **💡 Tip**: Start with the Limited Trial to test the integration, then upgrade based on your needs.

---

## 🚀 Running Locally

### 🖥️ Development Setup

```bash
# 1. Clone and navigate
git clone https://github.com/bluefoxlabsai/bfl-mcp-servers.git
cd bfl-mcp-servers/accuweather-mcp

# 2. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv sync

# 4. Set up environment
cp .env.example .env
# Edit .env with your AccuWeather API key

# 5. Run the server
uv run mcp-accuweather
```

### ⚡ Quick Commands

```bash
# Install dependencies
uv sync

# Run in STDIO mode (default - for AI assistants)
uv run mcp-accuweather

# Run in SSE mode (for web apps)
uv run mcp-accuweather --port 8000

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code  
uv run ruff check . --fix

# Type checking
uv run mypy src/
```

---

## 🎯 Usage

### 🔌 Transport Modes

<div align="center">

| Mode | Use Case | Command |
|------|----------|---------|
| **STDIO** 📡 | AI Assistants, Desktop Apps | `uv run mcp-accuweather` |
| **SSE** 🌐 | Web Apps, APIs, Remote Access | `uv run mcp-accuweather --port 8000` |

</div>

#### 🤖 STDIO Mode (AI Assistants)

```bash
# Global installation
mcp-accuweather

# With uv (from project directory)
uv run mcp-accuweather

# With environment variables
ACCUWEATHER_API_KEY=your-key uv run mcp-accuweather
```

#### 🌐 SSE Mode (Web Applications)

```bash
# Global installation
mcp-accuweather --port 8000

# With uv (from project directory)
uv run mcp-accuweather --port 8000

# Custom port
uv run mcp-accuweather --port 3000

# SSE endpoint will be available at: http://localhost:PORT/sse
```

### 🐳 Docker

#### Quick Start with Pre-built Image

```bash
# Run with SSE transport (default)
docker run -p 8000:8000 \
  -e ACCUWEATHER_API_KEY=your-api-key \
  bfljerum/accuweather-mcp:latest

# SSE endpoint available at: http://localhost:8000/sse
```

#### Build Locally

```bash
# Build the image
docker build -t accuweather-mcp .

# Run in STDIO mode
docker run -e ACCUWEATHER_API_KEY=your-key accuweather-mcp uv run mcp-accuweather

# Run in SSE mode (default)
docker run -p 8000:8000 -e ACCUWEATHER_API_KEY=your-key accuweather-mcp
```

---

## 🏗️ Kubernetes Deployment

### 🚀 Helm Installation

```bash
# Add to your cluster
cd accuweather-mcp/helm

# Install with Helm
helm install accuweather-mcp . \
  --namespace mcp-servers \
  --create-namespace \
  --set accuweather.apiKey=your-api-key \
  --set mcp.transport=sse

# Check deployment
kubectl get pods -n mcp-servers
kubectl get service -n mcp-servers
```

### 🔧 Configuration Options

```yaml
# values.yaml
mcp:
  transport: "sse"  # or "stdio"
  server:
    port: 8000

accuweather:
  apiKey: "your-api-key"
  baseUrl: "http://dataservice.accuweather.com"
  cache:
    ttl: 300
    maxSize: 1000

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

---

## 🧪 Available Tools

### 🔍 **Location Tools**

| Tool | Description | Example |
|------|-------------|---------|
| `search_locations` | Find locations by query | "New York", "10001", "40.7,-74.0" |
| `get_location_by_coordinates` | Reverse geocoding | lat: 40.7128, lon: -74.0060 |

### 🌤️ **Weather Tools**

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_current_weather` | Current conditions | location_key, language, details |
| `get_daily_forecast` | Multi-day forecast | location_key, days (1-15), metric |
| `get_hourly_forecast` | Hourly forecast | location_key, hours (1-120), metric |
| `get_weather_alerts` | Active alerts | location_key, language |
| `get_historical_weather` | Historical data | location_key, date (YYYY-MM-DD) |

### 📊 **Example Workflow**

```python
# 1. Search for a location
search_locations(query="San Francisco, CA")
# Returns: location_key="347629"

# 2. Get current weather
get_current_weather(location_key="347629")
# Returns: Current temperature, conditions, humidity, etc.

# 3. Get 5-day forecast
get_daily_forecast(location_key="347629", days=5)
# Returns: Daily high/low temps, conditions, precipitation

# 4. Check for weather alerts
get_weather_alerts(location_key="347629")
# Returns: Any active weather warnings or advisories
```

---

## 🎛️ Client Configuration

### 🤖 Claude Desktop (STDIO)

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "accuweather": {
      "command": "uv",
      "args": ["run", "mcp-accuweather"],
      "cwd": "/path/to/your/project",
      "env": {
        "ACCUWEATHER_API_KEY": "your-api-key"
      }
    }
  }
}
```

### 🌐 SSE Client Integration

```python
import aiohttp
import json

# Call MCP server via SSE
async def get_weather():
    async with aiohttp.ClientSession() as session:
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_current_weather",
                "arguments": {
                    "location_key": "347629"
                }
            }
        }
        
        async with session.post(
            "http://localhost:8000/sse",
            json=message,
            headers={'Accept': 'text/event-stream'}
        ) as response:
            async for line in response.content:
                if line:
                    print(line.decode())
```

---

## 🔒 Security & Best Practices

### 🛡️ Production Deployment

1. **Use secrets** for API keys instead of environment variables
2. **Enable resource limits** to prevent resource exhaustion
3. **Use specific image tags** instead of `latest`
4. **Configure security contexts** with non-root users
5. **Set up monitoring** and alerting for API usage

### 🚦 Rate Limiting

AccuWeather API has rate limits based on your plan:
- **Limited Trial**: 50 calls/day
- **Core Weather**: 1,000 calls/day  
- **Standard**: 5,000 calls/day

The server includes built-in caching to minimize API calls.

---

## 📊 Performance

| Feature | STDIO Mode | SSE Mode |
|---------|------------|----------|
| **Latency** | ~50ms | ~100ms |
| **Throughput** | Single client | Multiple clients |
| **Memory** | Process-based | Always running |
| **Network** | Local only | Network accessible |
| **Caching** | In-memory | Shared cache |

---

## 🤝 Support

- 📝 **Issues**: [GitHub Issues](https://github.com/bluefoxlabsai/bfl-mcp-servers/issues)
- 📧 **Email**: support@bluefoxlabs.ai  
- 🌐 **Website**: [Blue Fox Labs](https://bluefoxlabs.ai)
- 📚 **AccuWeather API Docs**: [AccuWeather Developer Portal](https://developer.accuweather.com/)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by [Blue Fox Labs AI](https://bluefoxlabs.ai)**

*Empowering AI with real-time weather intelligence*

</div>
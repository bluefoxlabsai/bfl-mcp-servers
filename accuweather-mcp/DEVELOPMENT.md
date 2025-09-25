# AccuWeather MCP Development Guide

This document provides information for developers working on the AccuWeather MCP server.

## Project Structure

```
accuweather-mcp/
├── src/mcp_accuweather/          # Main source code
│   ├── __init__.py               # Entry point and CLI
│   ├── server.py                 # FastMCP server implementation
│   ├── client.py                 # AccuWeather API client
│   ├── models.py                 # Pydantic models
│   └── exceptions.py             # Custom exceptions
├── tests/                        # Test suite
│   ├── test_server.py           # Server tests
│   └── test_client.py           # Client tests
├── scripts/                      # Development scripts
│   ├── setup_dev.sh             # Development environment setup
│   ├── start_dev_server.sh      # Start development server
│   ├── test_server.py           # Manual testing script
│   ├── integration_test.py      # Integration tests
│   └── build_and_push.sh        # Docker build and push
├── helm/                         # Kubernetes Helm charts
│   ├── Chart.yaml               # Chart metadata
│   ├── values.yaml              # Default values
│   ├── templates/               # Kubernetes templates
│   └── install.sh               # Installation script
├── .github/workflows/           # CI/CD workflows
├── Dockerfile                   # Container image
├── pyproject.toml              # Python project configuration
└── README.md                   # User documentation
```

## Development Setup

1. **Prerequisites**
   - Python 3.10+
   - uv package manager
   - AccuWeather API key

2. **Quick Setup**
   ```bash
   ./scripts/setup_dev.sh
   ```

3. **Manual Setup**
   ```bash
   # Install dependencies
   uv sync --dev
   
   # Create environment file
   cp .env.example .env
   # Edit .env and add your API key
   
   # Install pre-commit hooks
   uv run pre-commit install
   ```

## Development Workflow

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mcp_accuweather

# Run specific test file
uv run pytest tests/test_client.py -v
```

### Code Quality
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/
```

### Running the Server

#### STDIO Mode (for MCP clients)
```bash
uv run mcp-accuweather
```

#### SSE Mode (for web/HTTP clients)
```bash
uv run mcp-accuweather --port 8000
# or
./scripts/start_dev_server.sh --port 8000
```

### Testing the Server
```bash
# Environment check
python scripts/integration_test.py --env-only

# Full integration test (requires running server)
python scripts/integration_test.py --port 8000

# Manual API testing
python scripts/test_server.py
```

## API Client Architecture

The `AccuWeatherClient` class provides:

- **Async HTTP client** using httpx
- **Automatic caching** with TTL and size limits
- **Rate limiting** and error handling
- **Comprehensive error types** for different API responses
- **Context manager support** for proper resource cleanup

### Key Methods
- `search_locations()` - Find locations by name/coordinates
- `get_current_conditions()` - Current weather data
- `get_daily_forecast()` - Multi-day forecasts
- `get_hourly_forecast()` - Hourly forecasts
- `get_weather_alerts()` - Active weather alerts
- `get_historical_weather()` - Historical data (premium)

## MCP Server Architecture

The server uses FastMCP framework and provides:

- **7 MCP tools** for weather data access
- **SSE transport** for web integration
- **STDIO transport** for MCP clients
- **Pydantic models** for request/response validation
- **Comprehensive error handling** and logging

### Available Tools
1. `search_locations` - Location search
2. `get_current_conditions` - Current weather
3. `get_daily_forecast` - Daily forecasts
4. `get_hourly_forecast` - Hourly forecasts
5. `get_weather_alerts` - Weather alerts
6. `get_historical_weather` - Historical data
7. `get_location_key` - Quick location lookup

## Docker & Deployment

### Building Images
```bash
# Build and push to registry
./scripts/build_and_push.sh --tag v1.0.0

# Build locally
docker build -t accuweather-mcp .
```

### Kubernetes Deployment
```bash
# Install with Helm
cd helm
./install.sh

# Or manually
helm install accuweather-mcp . \
  --set secret.accuweatherApiKey="your-api-key"
```

## Configuration

### Environment Variables
- `ACCUWEATHER_API_KEY` - Required API key
- `ACCUWEATHER_BASE_URL` - API base URL (optional)

### Helm Values
See `helm/values.yaml` for all configuration options including:
- Resource limits and requests
- Horizontal Pod Autoscaling
- Ingress configuration
- Service configuration

## Contributing

1. **Fork and clone** the repository
2. **Create a feature branch** from `develop`
3. **Make changes** following the coding standards
4. **Add tests** for new functionality
5. **Run the test suite** and ensure all tests pass
6. **Submit a pull request** to `develop` branch

### Coding Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Add docstrings for public methods
- Maintain test coverage above 80%
- Use meaningful commit messages

### Release Process
1. Merge `develop` to `main`
2. Tag the release: `git tag v1.0.0`
3. Push tags: `git push --tags`
4. GitHub Actions will build and publish automatically

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Verify key is set in `.env` file
   - Check key has required permissions
   - Ensure key is not expired

2. **Rate Limiting**
   - AccuWeather has strict rate limits
   - Use caching to reduce API calls
   - Consider upgrading API plan

3. **Network Issues**
   - Check firewall settings
   - Verify DNS resolution
   - Test with curl/httpx directly

### Debug Mode
Set environment variable for detailed logging:
```bash
export FASTMCP_LOG_LEVEL=DEBUG
```

### Performance Tuning
- Adjust cache TTL and size in client
- Configure appropriate resource limits
- Use HPA for auto-scaling under load

## API Reference

See the AccuWeather API documentation:
- [Developer Portal](https://developer.accuweather.com/)
- [API Reference](https://developer.accuweather.com/accuweather-current-conditions-api/apis)
- [Rate Limits](https://developer.accuweather.com/api-limits-pricing)
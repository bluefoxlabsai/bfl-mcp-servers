# SharePoint MCP Development Guide

This guide covers development setup, testing, and contribution guidelines for the SharePoint MCP project.

## Development Setup

### Prerequisites

- Python 3.10+
- UV package manager
- Docker (optional, for containerized development)
- Access to SharePoint Online or SharePoint Server
- Azure AD App Registration (for SharePoint Online)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sharepoint-mcp
   ```

2. **Install dependencies**
   ```bash
   uv sync --group dev
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your SharePoint credentials
   ```

4. **Install pre-commit hooks**
   ```bash
   uv run pre-commit install
   ```

## Running the Server

### STDIO Mode (for MCP clients)
```bash
uv run mcp-sharepoint
```

### HTTP Mode (for web clients)
```bash
# SSE transport
uv run mcp-sharepoint --transport sse --host 0.0.0.0 --port 8000

# Streamable HTTP transport
uv run mcp-sharepoint --transport streamable-http --host 0.0.0.0 --port 8000
```

### With verbose logging
```bash
uv run mcp-sharepoint --transport sse --verbose
```

## Testing

### Run all tests
```bash
uv run pytest
```

### Run with coverage
```bash
uv run pytest --cov=src --cov-report=html
```

### Run specific test file
```bash
uv run pytest tests/test_sharepoint_client.py -v
```

### Run linting and formatting
```bash
uv run ruff check .
uv run black .
uv run mypy .
```

## Project Structure

```
sharepoint-mcp/
├── src/mcp_sharepoint/          # Main package
│   ├── __init__.py              # CLI entry point
│   ├── exceptions.py            # Custom exceptions
│   ├── models/                  # Data models
│   │   └── sharepoint.py        # SharePoint data models
│   ├── sharepoint/              # SharePoint integration
│   │   └── client.py            # SharePoint client
│   ├── servers/                 # MCP server implementations
│   │   └── main_mcp.py          # Main FastMCP server
│   └── utils/                   # Utility modules
│       ├── env.py               # Environment utilities
│       ├── lifecycle.py         # Lifecycle management
│       └── logging.py           # Logging utilities
├── tests/                       # Test files
├── helm/                        # Kubernetes Helm chart
├── pyproject.toml               # Project configuration
├── Dockerfile                   # Container image
└── README.md                    # Project documentation
```

## Adding New Features

### Adding a new SharePoint tool

1. **Define the input model** in `servers/main_mcp.py`:
   ```python
   class NewToolInput(BaseModel):
       param1: str = Field(description="Parameter description")
       param2: Optional[int] = Field(default=None, description="Optional parameter")
   ```

2. **Implement the client method** in `sharepoint/client.py`:
   ```python
   async def new_operation(self, param1: str, param2: Optional[int] = None) -> SomeModel:
       """Perform new SharePoint operation."""
       context = await self._get_context()
       # Implementation here
       return result
   ```

3. **Add the MCP tool** in `servers/main_mcp.py`:
   ```python
   @mcp.tool()
   async def sharepoint_new_tool(input_data: NewToolInput) -> Dict[str, Any]:
       """Description of the new tool."""
       try:
           client = get_sharepoint_client()
           result = await client.new_operation(input_data.param1, input_data.param2)
           return {"result": result.model_dump()}
       except Exception as e:
           logger.error(f"Error in new tool: {e}")
           return {"error": str(e)}
   ```

4. **Add tests** in `tests/`:
   ```python
   async def test_new_tool():
       """Test the new tool functionality."""
       # Test implementation
   ```

### Adding new data models

1. Create new model classes in `models/sharepoint.py`:
   ```python
   class NewModel(BaseModel):
       """Description of the new model."""
       field1: str = Field(description="Field description")
       field2: Optional[datetime] = Field(default=None, description="Optional field")
   ```

## Docker Development

### Build local image
```bash
docker build -t sharepoint-mcp .
```

### Run with Docker
```bash
docker run --rm -p 8000:8000 --env-file .env sharepoint-mcp
```

### Test Docker image
```bash
docker run --rm sharepoint-mcp --help
```

## Kubernetes Development

### Test Helm chart
```bash
cd helm
./install.sh --dry-run
```

### Deploy to local cluster
```bash
cd helm
./install.sh sharepoint-mcp-dev
```

### Clean up
```bash
cd helm
./uninstall.sh sharepoint-mcp-dev
```

## Code Quality

### Pre-commit hooks
The project uses pre-commit hooks to ensure code quality:
- `ruff` for linting and formatting
- `mypy` for type checking
- Standard hooks for trailing whitespace, file endings, etc.

### Code style
- Follow PEP 8 guidelines
- Use type hints for all functions and methods
- Add docstrings for all public functions and classes
- Keep line length under 88 characters

### Error handling
- Use custom exceptions from `exceptions.py`
- Log errors appropriately
- Return structured error responses from MCP tools

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the development guidelines
4. **Add tests** for new functionality
5. **Run the test suite**: `uv run pytest`
6. **Run linting**: `uv run pre-commit run --all-files`
7. **Commit your changes**: `git commit -m 'Add amazing feature'`
8. **Push to the branch**: `git push origin feature/amazing-feature`
9. **Submit a pull request**

## Debugging

### Enable debug logging
```bash
export MCP_VERBOSE=true
uv run mcp-sharepoint --transport sse -vv
```

### Common issues

1. **Authentication errors**: Check Azure AD app permissions and credentials
2. **Import errors**: Ensure all dependencies are installed with `uv sync`
3. **Connection issues**: Verify SharePoint site URL and network connectivity

### Debugging with Docker
```bash
docker run --rm -it --env-file .env sharepoint-mcp /bin/sh
```

## Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new features and fixes
3. **Create a git tag**: `git tag v1.0.0`
4. **Push tag**: `git push origin v1.0.0`
5. **Build and publish** Docker image
6. **Publish to PyPI** (if applicable)

## Support

- **Issues**: [GitHub Issues](https://github.com/sooperset/mcp-sharepoint/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sooperset/mcp-sharepoint/discussions)
- **Documentation**: Check the README.md and this development guide
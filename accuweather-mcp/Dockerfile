# AccuWeather MCP Server Dockerfile
# Multi-architecture support: linux/amd64, linux/arm64

FROM astral/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY pyproject.toml .
COPY uv.lock .
COPY src/ ./src/

# Create a minimal README for the build
RUN echo "# AccuWeather MCP Server" > README.md

# Install dependencies using uv
RUN uv sync --frozen

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port for SSE transport
EXPOSE 8000

# Default command (SSE mode) - using uv run with port
CMD ["uv", "run", "mcp-accuweather", "--port", "8000"]

# Usage examples:
# SSE mode (default): docker run -p 8000:8000 accuweather-mcp
# STDIO mode: docker run accuweather-mcp uv run mcp-accuweather
# With environment: docker run -e ACCUWEATHER_API_KEY=your-key -p 8000:8000 accuweather-mcp
# SSE endpoint available at: http://localhost:8000/sse
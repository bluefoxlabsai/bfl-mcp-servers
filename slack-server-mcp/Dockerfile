# Python Slack MCP Server Dockerfile
# Multi-architecture support: linux/amd64, linux/arm64

FROM astral/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Install system dependencies including curl for health checks
# and clean up package cache to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY pyproject.toml .
COPY uv.lock .
COPY slack_mcp_server/ ./slack_mcp_server/

# Create a minimal README for the build (since the real one is dockerignored)
RUN echo "# Slack MCP Server" > README.md

# Install dependencies using uv
RUN uv sync --frozen

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port for SSE transport
EXPOSE 8000

# Default command (SSE mode) - using uv run with port
CMD ["uv", "run", "slack-mcp-server", "--port", "8000"]

# Usage examples:
# SSE mode (default): docker run -p 8000:8000 slack-server-mcp
# STDIO mode: docker run slack-server-mcp uv run slack-mcp-server
# With environment: docker run -e SLACK_BOT_TOKEN=xoxb-... -e SLACK_USER_TOKEN=xoxp-... -p 8000:8000 slack-server-mcp
# SSE endpoint available at: http://localhost:8000/sse
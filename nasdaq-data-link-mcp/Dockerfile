# Multi-stage build for smaller final image
FROM python:3.13-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --user "mcp[cli]" nasdaq-data-link pycountry

# Production stage
FROM python:3.13-slim

# Install runtime dependencies and create non-root user
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1001 appuser \
    && useradd --uid 1001 --gid appuser --shell /bin/bash --create-home appuser

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Set up application directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/appuser/.local/bin:$PATH

# Create directory for logs and set permissions
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('0.0.0.0', 8000)); s.close()" || exit 1

# Use tini as init system and run the application
ENTRYPOINT ["tini", "--"]
CMD ["python", "nasdaq_data_link_mcp_os/server.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]

# Add labels for better maintainability
LABEL maintainer="BlueFox Labs <contact@bluefoxlabs.ai>" \
      version="0.2.1" \
      description="NASDAQ Data Link MCP Server" \
      org.opencontainers.image.source="https://github.com/bluefoxlabsai/bfl-mcp-servers" \
      org.opencontainers.image.documentation="https://github.com/bluefoxlabsai/bfl-mcp-servers/tree/main/nasdaq-data-link-mcp"

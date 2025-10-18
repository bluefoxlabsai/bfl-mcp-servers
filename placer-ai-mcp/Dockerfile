# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.10-alpine AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install system dependencies if needed
RUN apk add --no-cache curl

# Generate proper TOML lockfile first
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv lock

# Install the project's dependencies using the lockfile
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev --no-editable

# Remove unnecessary files from the virtual environment before copying
RUN find /app/.venv -name "*.pyc" -type f -delete \
    && find /app/.venv -name "__pycache__" -type d -exec rm -rf {} + \
    && find /app/.venv -name "*.egg-info" -type d -exec rm -rf {} + \
    || true

# Create a non-root user for running the application
RUN addgroup -g 1000 appuser && adduser -u 1000 -G appuser -D appuser
RUN chown -R appuser:appuser /app
USER appuser

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Set environment variables
ENV PYTHONPATH="/app/src"
ENV MCP_TRANSPORT="streamable-http"
ENV HOST="0.0.0.0"
ENV PORT="8000"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose the port
EXPOSE 8000

# Run the application using UV
CMD ["uv", "run", "--frozen", "python", "-m", "mcp_placer_ai.server"]
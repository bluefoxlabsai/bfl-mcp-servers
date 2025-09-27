# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim AS uv

# Set environment variables for playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

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
    uv sync --frozen --no-dev --editable

# Install playwright browsers
RUN uv run playwright install chromium

# Remove unnecessary files from the virtual environment before copying
RUN find /app/.venv -name '__pycache__' -type d -exec rm -rf {} + && \
    find /app/.venv -name '*.pyc' -delete && \
    find /app/.venv -name '*.pyo' -delete && \
    echo "Cleaned up .venv"

# Final stage
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

# Create a non-root user 'app'
RUN useradd -m -s /bin/bash app
WORKDIR /home/app
USER app

# Copy only the virtual environment and essential files
COPY --from=uv --chown=app:app /app/.venv /app/.venv
COPY --from=uv --chown=app:app /app/src /app/src
COPY --from=uv --chown=app:app /app/README.md /app/README.md
COPY --from=uv /ms-playwright /ms-playwright

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Expose port for Streamable HTTP transport
EXPOSE 8000

ENTRYPOINT ["/app/.venv/bin/mcp-web-browser", "--transport", "streamable-http", "--verbose", "--host", "0.0.0.0", "--port", "8000"]
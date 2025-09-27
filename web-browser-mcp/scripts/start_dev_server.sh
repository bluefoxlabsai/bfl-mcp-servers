#!/bin/bash

# Start development server for Web Browser MCP
#
# Usage:
#   ./start_dev_server.sh
#
# This script starts the MCP server in development mode with streamable HTTP transport.

set -e

echo "Starting Web Browser MCP development server..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first."
    exit 1
fi

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "Installing dependencies..."
    uv sync
fi

# Start the server
echo "Server will be available at: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo "MCP endpoint: http://localhost:8000/mcp"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uv run mcp-web-browser --transport streamable-http --port 8000 --verbose
#!/bin/bash
set -e

# Development server startup script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
PORT=8000
MODE="sse"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --stdio)
            MODE="stdio"
            shift
            ;;
        --sse)
            MODE="sse"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --port PORT    Port for SSE server (default: 8000)"
            echo "  --stdio        Start in STDIO mode"
            echo "  --sse          Start in SSE mode (default)"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

cd "$PROJECT_DIR"

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        echo "📝 Please edit .env file and add your AccuWeather API key"
    else
        echo "❌ No .env.example file found"
        exit 1
    fi
fi

# Check for API key
if ! grep -q "ACCUWEATHER_API_KEY=" .env || grep -q "ACCUWEATHER_API_KEY=$" .env; then
    echo "❌ ACCUWEATHER_API_KEY not set in .env file"
    echo "Please add your AccuWeather API key to the .env file:"
    echo "ACCUWEATHER_API_KEY=your_api_key_here"
    exit 1
fi

echo "🚀 Starting AccuWeather MCP Server..."
echo "📁 Project directory: $PROJECT_DIR"
echo "🔧 Mode: $MODE"

# Sync dependencies
echo "📦 Syncing dependencies..."
uv sync

if [[ "$MODE" == "stdio" ]]; then
    echo "📡 Starting in STDIO mode..."
    uv run mcp-accuweather
else
    echo "📡 Starting SSE server on port $PORT..."
    echo "🌐 SSE endpoint: http://localhost:$PORT/sse"
    echo "❤️  Health check: http://localhost:$PORT/health"
    uv run mcp-accuweather --port "$PORT"
fi
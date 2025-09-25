#!/bin/bash
set -e

# Development environment setup script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Setting up AccuWeather MCP development environment..."
echo "📁 Project directory: $PROJECT_DIR"

cd "$PROJECT_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is available"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --dev

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your AccuWeather API key:"
    echo "   ACCUWEATHER_API_KEY=your_api_key_here"
else
    echo "✅ .env file already exists"
fi

# Install pre-commit hooks if available
if [[ -f ".pre-commit-config.yaml" ]]; then
    echo "🔧 Installing pre-commit hooks..."
    uv run pre-commit install
fi

# Run tests to verify setup
echo "🧪 Running basic tests..."
if uv run python -m pytest tests/ -v; then
    echo "✅ Tests passed"
else
    echo "⚠️  Some tests failed, but setup is complete"
fi

# Check environment
echo "🔍 Checking environment..."
uv run python scripts/integration_test.py --env-only

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your AccuWeather API key"
echo "2. Start the development server: ./scripts/start_dev_server.sh"
echo "3. Run tests: uv run pytest"
echo "4. Run integration tests: python scripts/integration_test.py"
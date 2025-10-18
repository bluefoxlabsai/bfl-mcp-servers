# Contributing to MCP Placer.ai

Thank you for your interest in contributing to MCP Placer.ai! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. Make sure you have Python 3.10+ installed
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
1. Fork the repository
1. Clone your fork: `git clone https://github.com/YOUR-USERNAME/placer-ai-mcp.git`
1. Add the upstream remote: `git remote add upstream https://github.com/bluefoxlabsai/placer-ai-mcp.git`
1. Install dependencies:

    ```sh
    uv sync
    uv sync --frozen --all-extras --dev
    ```

1. Activate the virtual environment:

    __macOS and Linux__:

    ```sh
    source .venv/bin/activate
    ```

    __Windows__:

    ```powershell
    .venv\Scripts\activate.ps1
    ```

## Testing

Before submitting a pull request, ensure all tests pass:

```sh
# Run unit tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run integration tests (requires API key)
export PLACER_AI_API_KEY=your_test_api_key
uv run pytest tests/integration/
```

## Code Quality

We use several tools to maintain code quality:

```sh
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run mypy src/

# Run all quality checks
uv run pre-commit run --all-files
```

## Running the Server Locally

```sh
# Set environment variables
export PLACER_AI_API_KEY=your_api_key

# Run with different transports
uv run mcp-placer-ai --transport stdio
uv run mcp-placer-ai --transport streamable-http --host 0.0.0.0 --port 8000
uv run mcp-placer-ai --transport sse --host 0.0.0.0 --port 8000
```

## Docker Development

```sh
# Build local image
docker build -t placer-ai-mcp:dev .

# Run with your API key
docker run --rm -p 8000:8000 \
  -e PLACER_AI_API_KEY=your_api_key \
  placer-ai-mcp:dev
```

## Kubernetes Development

```sh
# Test Helm chart locally
helm template . --debug --set placerAI.apiKey=test-key

# Install in development namespace
./helm/install.sh placer-ai-mcp-dev --namespace development
```

## Making Changes

1. Create a new branch for your feature/fix:
   ```sh
   git checkout -b feature/your-feature-name
   ```

1. Make your changes following these guidelines:
   - Follow existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed
   - Use clear, descriptive commit messages

1. Test your changes thoroughly:
   ```sh
   uv run pytest
   uv run ruff check
   uv run ruff format --check
   ```

1. Commit your changes:
   ```sh
   git add .
   git commit -m "feat: add new feature description"
   ```

1. Push to your fork:
   ```sh
   git push origin feature/your-feature-name
   ```

1. Create a pull request from your fork to the main repository

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include tests for new functionality
- Ensure all CI checks pass
- Keep changes focused and atomic
- Update documentation if needed

## Issue Reporting

When reporting issues, please include:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Relevant logs or error messages

## Feature Requests

For feature requests, please:

- Check if the feature already exists
- Describe the use case clearly
- Explain why the feature would be beneficial
- Consider implementation approaches

## Code Style

We follow these conventions:

- Use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- Type hints for all public functions
- Docstrings for public classes and functions
- Clear variable and function names
- Keep functions focused and small

## Documentation

- Update README.md for user-facing changes
- Add docstrings for new public APIs
- Update Helm chart documentation for deployment changes
- Include examples for new features

## Release Process

Releases are handled by maintainers:

1. Update version in `pyproject.toml`
1. Update CHANGELOG.md
1. Create release tag
1. GitHub Actions builds and publishes Docker image
1. Helm chart is updated and published

## Community

- Be respectful and inclusive
- Help others in discussions
- Share knowledge and best practices
- Follow the code of conduct

## Getting Help

If you need help:

- Check existing issues and discussions
- Ask questions in GitHub issues
- Contact maintainers directly for urgent matters

Thank you for contributing to MCP Placer.ai!
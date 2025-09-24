#!/bin/bash

# Build and push Docker image for Slack MCP Server
# Usage: ./build-docker.sh [tag]

set -e

# Default values
DEFAULT_TAG="0.1.5"
REGISTRY="docker.io"
REPO_OWNER="bfljerum"
IMAGE_NAME="slack-server-mcp"

# Use provided tag or default
TAG=${1:-$DEFAULT_TAG}
FULL_IMAGE_NAME="${REGISTRY}/${REPO_OWNER}/${IMAGE_NAME}"

echo "🐳 Building Docker image for Slack MCP Server"
echo "📦 Image: ${FULL_IMAGE_NAME}:${TAG}"
echo "🏗️  Building multi-architecture image (amd64, arm64)..."

# Build multi-architecture image
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag "${FULL_IMAGE_NAME}:${TAG}" \
  --tag "${FULL_IMAGE_NAME}:latest" \
  --push \
  .

echo "✅ Successfully built and pushed:"
echo "   - ${FULL_IMAGE_NAME}:${TAG}"
echo "   - ${FULL_IMAGE_NAME}:latest"

echo ""
echo "🚀 Usage examples:"
echo "   docker run -p 8000:8000 ${FULL_IMAGE_NAME}:${TAG}"
echo "   docker run -e SLACK_BOT_TOKEN=xoxb-... -e SLACK_USER_TOKEN=xoxp-... -p 8000:8000 ${FULL_IMAGE_NAME}:${TAG}"
echo ""
echo "🌐 SSE endpoint will be available at: http://localhost:8000/sse"
#!/bin/bash

# Build and push Docker image for Web Browser MCP
#
# Usage:
#   ./build_and_push.sh [tag]
#
# Environment Variables:
#   DOCKER_REGISTRY - Docker registry (optional, defaults to docker.io)
#   DOCKER_REPO - Docker repository (optional, defaults to mcp-web-browser)
#
# Examples:
#   ./build_and_push.sh                    # Build and push with latest tag
#   ./build_and_push.sh v1.0.0             # Build and push with specific tag
#   DOCKER_REGISTRY=ghcr.io ./build_and_push.sh  # Use GitHub Container Registry

set -e

# Default values
TAG=${1:-"latest"}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"docker.io"}
DOCKER_REPO=${DOCKER_REPO:-"mcp-web-browser"}
IMAGE_NAME="$DOCKER_REGISTRY/$DOCKER_REPO:$TAG"

echo "Building Docker image: $IMAGE_NAME"

# Build the image
docker build -t "$IMAGE_NAME" ..

# Push the image
echo "Pushing Docker image: $IMAGE_NAME"
docker push "$IMAGE_NAME"

echo "✅ Successfully built and pushed: $IMAGE_NAME"
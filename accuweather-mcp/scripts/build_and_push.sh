#!/bin/bash
set -e

# Build and push script for AccuWeather MCP server
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
REGISTRY="docker.io"
REPOSITORY="bfljerum/accuweather-mcp"
TAG="latest"
PLATFORM="linux/amd64,linux/arm64"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --repository)
            REPOSITORY="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --registry REGISTRY     Docker registry (default: docker.io)"
            echo "  --repository REPO       Repository name (default: bfljerum/accuweather-mcp)"
            echo "  --tag TAG              Image tag (default: latest)"
            echo "  --platform PLATFORMS   Target platforms (default: linux/amd64,linux/arm64)"
            echo "  --help                 Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

IMAGE_NAME="${REGISTRY}/${REPOSITORY}:${TAG}"

echo "🏗️  Building AccuWeather MCP Docker image..."
echo "📦 Image: $IMAGE_NAME"
echo "🏗️  Platform: $PLATFORM"
echo "📁 Context: $PROJECT_DIR"

cd "$PROJECT_DIR"

# Build and push multi-platform image
docker buildx build \
    --platform "$PLATFORM" \
    --tag "$IMAGE_NAME" \
    --push \
    .

echo "✅ Successfully built and pushed: $IMAGE_NAME"

# Also tag as latest if not already latest
if [[ "$TAG" != "latest" ]]; then
    LATEST_IMAGE="${REGISTRY}/${REPOSITORY}:latest"
    echo "🏷️  Tagging as latest: $LATEST_IMAGE"
    
    docker buildx build \
        --platform "$PLATFORM" \
        --tag "$LATEST_IMAGE" \
        --push \
        .
    
    echo "✅ Successfully tagged and pushed: $LATEST_IMAGE"
fi

echo "🎉 Build and push completed successfully!"
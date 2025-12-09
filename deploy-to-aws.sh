#!/bin/bash
set -e

# AWS Deployment Script for Enhanced Chroma MCP Server
# Usage: ./deploy-to-aws.sh [version]

VERSION=${1:-latest}
CONTAINER_NAME="chroma-mcp"
IMAGE_NAME="ghcr.io/l0rdhelmchen/chroma-mcp"
BACKUP_TAG="backup-$(date +%Y%m%d-%H%M%S)"

echo "🚀 Deploying Enhanced Chroma MCP Server to AWS"
echo "================================================"
echo "Version: $VERSION"
echo "Container: $CONTAINER_NAME"
echo "Image: $IMAGE_NAME:$VERSION"
echo ""

# Configuration (adjust for your AWS server!)
# ============================================
CHROMA_HOST="${CHROMA_HOST:-your-chroma-server.internal}"
CHROMA_PORT="${CHROMA_PORT:-8000}"
CHROMA_SSL="${CHROMA_SSL:-false}"
CHROMA_CLIENT_TYPE="${CHROMA_CLIENT_TYPE:-http}"

# Enhanced connectivity settings
CHROMA_DEBUG="${CHROMA_DEBUG:-true}"
CHROMA_CONNECTION_TIMEOUT="${CHROMA_CONNECTION_TIMEOUT:-60}"
CHROMA_RETRY_ATTEMPTS="${CHROMA_RETRY_ATTEMPTS:-5}"

echo "📋 Configuration:"
echo "  CHROMA_HOST: $CHROMA_HOST"
echo "  CHROMA_PORT: $CHROMA_PORT"
echo "  CHROMA_SSL: $CHROMA_SSL"
echo "  CHROMA_DEBUG: $CHROMA_DEBUG"
echo "  TIMEOUT: ${CHROMA_CONNECTION_TIMEOUT}s"
echo "  RETRIES: $CHROMA_RETRY_ATTEMPTS"
echo ""

# Pre-deployment checks
# ====================
echo "🔍 Pre-deployment checks..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running or accessible"
    exit 1
fi

# Check if container exists
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    echo "✅ Found running container: $CONTAINER_NAME"
    EXISTING_CONTAINER=true
else
    echo "ℹ️  No existing container found"
    EXISTING_CONTAINER=false
fi

# Pull new image
# ==============
echo ""
echo "📥 Pulling new image..."
if docker pull "$IMAGE_NAME:$VERSION"; then
    echo "✅ Successfully pulled $IMAGE_NAME:$VERSION"
else
    echo "❌ Failed to pull image"
    exit 1
fi

# Backup existing container
# =========================
if [ "$EXISTING_CONTAINER" = true ]; then
    echo ""
    echo "💾 Creating backup..."

    # Tag current image as backup
    CURRENT_IMAGE=$(docker inspect "$CONTAINER_NAME" --format='{{.Image}}')
    docker tag "$CURRENT_IMAGE" "$IMAGE_NAME:$BACKUP_TAG"
    echo "✅ Created backup: $IMAGE_NAME:$BACKUP_TAG"

    # Export container logs
    docker logs "$CONTAINER_NAME" > "chroma-mcp-logs-backup-$(date +%Y%m%d-%H%M%S).log" 2>&1
    echo "✅ Exported logs to backup file"

    # Stop and remove existing container
    echo ""
    echo "🛑 Stopping existing container..."
    docker stop "$CONTAINER_NAME"
    docker rm "$CONTAINER_NAME"
    echo "✅ Container stopped and removed"
fi

# Deploy new container
# ===================
echo ""
echo "🚀 Starting new container with enhanced connectivity..."

# Check if we should use CloudWatch logging
if command -v aws &> /dev/null && [ -n "$AWS_REGION" ]; then
    echo "📊 Using CloudWatch logging"
    LOGGING_OPTIONS="--log-driver=awslogs --log-opt awslogs-group=/aws/docker/chroma-mcp --log-opt awslogs-region=$AWS_REGION --log-opt awslogs-stream=chroma-mcp-$(date +%Y%m%d)"
else
    echo "📋 Using JSON file logging"
    LOGGING_OPTIONS="--log-driver json-file --log-opt max-size=10m --log-opt max-file=3"
fi

# Start new container
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    $LOGGING_OPTIONS \
    -e CHROMA_CLIENT_TYPE="$CHROMA_CLIENT_TYPE" \
    -e CHROMA_HOST="$CHROMA_HOST" \
    -e CHROMA_PORT="$CHROMA_PORT" \
    -e CHROMA_SSL="$CHROMA_SSL" \
    -e CHROMA_DEBUG="$CHROMA_DEBUG" \
    -e CHROMA_CONNECTION_TIMEOUT="$CHROMA_CONNECTION_TIMEOUT" \
    -e CHROMA_RETRY_ATTEMPTS="$CHROMA_RETRY_ATTEMPTS" \
    "$IMAGE_NAME:$VERSION"

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully"
else
    echo "❌ Failed to start container"
    exit 1
fi

# Post-deployment verification
# ===========================
echo ""
echo "🔍 Post-deployment verification..."

# Wait for container to start
echo "⏳ Waiting for container to initialize..."
sleep 10

# Check container status
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "✅ Container is running"
else
    echo "❌ Container is not running"
    echo "📋 Container logs:"
    docker logs "$CONTAINER_NAME" 2>&1 | tail -20
    exit 1
fi

# Show enhanced logs
echo ""
echo "📋 Container logs (last 20 lines):"
docker logs "$CONTAINER_NAME" 2>&1 | tail -20

# Check for success indicators
echo ""
echo "🔍 Checking for enhanced connectivity features..."
if docker logs "$CONTAINER_NAME" 2>&1 | grep -q "✅.*Chroma client initialized successfully"; then
    echo "✅ Enhanced connectivity features are working"
else
    echo "⚠️  Enhanced connectivity features may not be working properly"
    echo "📋 Debug information:"
    docker logs "$CONTAINER_NAME" 2>&1 | grep -E "(❌|⚠️|ERROR|Failed)" | tail -5
fi

# Health check
echo ""
echo "🏥 Performing health check..."
sleep 5

if docker ps | grep -q "$CONTAINER_NAME.*Up"; then
    echo "✅ Health check passed"

    # Show connection status from logs
    if docker logs "$CONTAINER_NAME" 2>&1 | grep -q "✅.*Connection health check passed"; then
        echo "✅ Chroma database connection verified"
    else
        echo "⚠️  Chroma database connection status unclear - check logs"
    fi
else
    echo "❌ Health check failed"
    exit 1
fi

# Deployment summary
echo ""
echo "🎉 Deployment Summary"
echo "===================="
echo "Status: ✅ SUCCESS"
echo "Container: $CONTAINER_NAME"
echo "Image: $IMAGE_NAME:$VERSION"
echo "Backup: $IMAGE_NAME:$BACKUP_TAG"
echo ""
echo "🔧 Management commands:"
echo "  View logs:     podman logs -f $CONTAINER_NAME"
echo "  Restart:       podman restart $CONTAINER_NAME"
echo "  Stop:          podman stop $CONTAINER_NAME"
echo "  Rollback:      podman stop $CONTAINER_NAME && podman rm $CONTAINER_NAME && podman run -d --name $CONTAINER_NAME --restart unless-stopped $IMAGE_NAME:$BACKUP_TAG"
echo ""
echo "📊 Monitoring:"
echo "  Status:        podman ps | grep $CONTAINER_NAME"
echo "  Stats:         podman stats $CONTAINER_NAME"
echo "  Health:        podman logs $CONTAINER_NAME 2>&1 | grep -E '(✅|❌|⚠️)' | tail -5"
echo ""

# Final connection test
echo "🔗 Testing enhanced connectivity features..."
if docker logs "$CONTAINER_NAME" 2>&1 | grep -q "🚀.*Starting MCP server"; then
    echo "✅ MCP server is running with enhanced connectivity"
    echo "💡 Enhanced features active:"
    echo "   - Retry logic with exponential backoff"
    echo "   - Detailed error logging and diagnostics"
    echo "   - Connection validation and health checks"
    echo "   - SSL/TLS debugging capabilities"
else
    echo "⚠️  MCP server status unclear - manual verification recommended"
fi

echo ""
echo "🎯 Deployment completed successfully!"
echo "💡 Next steps:"
echo "   1. Monitor logs: docker logs -f $CONTAINER_NAME"
echo "   2. Test your MCP client connections"
echo "   3. If issues occur, check troubleshooting guide in HTTP_CONNECTIVITY_IMPROVEMENTS.md"
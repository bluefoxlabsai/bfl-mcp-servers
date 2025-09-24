# Slack MCP Server Helm Chart Summary

## Overview
This Helm chart deploys the Slack MCP (Model Context Protocol) server on Kubernetes, enabling AI assistants to interact with Slack workspaces through a standardized protocol.

## Key Features
- **Dual Transport Support**: STDIO (default) for AI assistants, HTTP for web applications
- **Interactive Installation**: Easy setup with guided scripts
- **Production Ready**: Includes security contexts, resource limits, and autoscaling
- **Flexible Configuration**: Support for existing secrets or inline token configuration
- **Comprehensive Toolset**: 11 Slack tools for channels, messages, users, and search

## Quick Installation
```bash
./install.sh
```

## Transport Modes

### STDIO Mode (Default)
- **Best for**: AI assistants (Claude, ChatGPT), desktop applications
- **Access**: `kubectl exec -it <pod> -- uv run slack-mcp-server`
- **Service**: Automatically disabled

### HTTP Mode
- **Best for**: Web applications, remote access, APIs
- **Access**: HTTP endpoints on port 8000
- **Service**: Automatically enabled with health checks

## Configuration Highlights

### Security
- Non-root container execution (user 1000)
- Secret-based token management
- Safe search mode for production
- Resource limits and requests

### Scalability
- Horizontal Pod Autoscaler support
- Multiple replica configuration
- CPU and memory-based scaling

### Networking
- Ingress support with customizable rules
- Gateway API HTTPRoute compatibility
- Service mesh ready

## Available Slack Tools
1. **slack_list_channels** - List workspace channels
2. **slack_post_message** - Send messages to channels
3. **slack_reply_to_thread** - Reply to message threads
4. **slack_add_reaction** - Add emoji reactions
5. **slack_get_channel_history** - Retrieve channel messages
6. **slack_get_thread_replies** - Get thread conversations
7. **slack_get_users** - List workspace users
8. **slack_get_user_profiles** - Get user profile data
9. **slack_search_messages** - Advanced message search
10. **slack_search_channels** - Find channels by name
11. **slack_search_users** - Search for users

## Values Files
- `examples/values-dev.yaml.example` - Development environment
- `examples/values-prod.yaml.example` - Production environment

## Requirements
- Kubernetes 1.19+
- Helm 3.0+
- Slack Bot Token (`xoxb-...`)
- Slack User Token (`xoxp-...`)

## Support
- **Repository**: https://github.com/bluefoxlabsai/bfl-mcp-servers
- **Issues**: https://github.com/bluefoxlabsai/bfl-mcp-servers/issues
- **Documentation**: [helm/README.md](README.md)
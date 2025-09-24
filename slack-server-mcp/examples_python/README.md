# Python Examples for Slack MCP Server

This directory contains Python example scripts that demonstrate how to use the Slack MCP Server.

## Prerequisites

1. Install the required dependencies:
   ```bash
   # With uv (recommended)
   uv add python-dotenv aiohttp
   
   # Or with pip
   pip install python-dotenv aiohttp
   ```

2. Set up your environment variables in a `.env` file:
   ```bash
   EXAMPLES_SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
   EXAMPLES_SLACK_USER_TOKEN=xoxp-your-slack-user-token-here
   ```

## Examples

### 1. `get_users.py` - STDIO Transport

Demonstrates how to call the MCP server using STDIO transport (the default mode).

```bash
# From examples_python directory
python get_users.py

# Or with uv from project root
uv run python examples_python/get_users.py
```

This example:
- Starts the MCP server as a subprocess
- Calls the `slack_get_users` tool
- Displays the first 5 users from your Slack workspace

### 2. `get_users_sse.py` - SSE Transport

Demonstrates how to call the MCP server using Server-Sent Events (SSE) transport.

```bash
# From examples_python directory
python get_users_sse.py

# Or with uv from project root
uv run python examples_python/get_users_sse.py
```

This example:
- Starts the MCP server in SSE mode on port 3000
- Makes SSE requests to call the `slack_get_users` tool via `/sse` endpoint
- Displays the first 3 users from your Slack workspace
- Automatically stops the server when done

## Understanding the Output

Both examples will show:
- Whether the API call was successful (`OK: True/False`)
- The number of users returned
- Details about each user (name, real name, bot status)
- Pagination information if available

## Troubleshooting

1. **Token Issues**: Make sure your bot token starts with `xoxb-` and user token starts with `xoxp-`
2. **Permission Issues**: Ensure your bot has the necessary scopes in your Slack app configuration
3. **Network Issues**: For SSE example, make sure port 3000 is available

## Next Steps

You can modify these examples to:
- Call different MCP tools (e.g., `slack_list_channels`, `slack_search_messages`)
- Change the parameters (limit, filters, etc.)
- Build your own client applications
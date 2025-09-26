"""
Slack MCP Server

A FastMCP server that provides Slack API functionality.
This server exposes tools for interacting with Slack channels, messages, and users.
It requires Slack Bot Token and User Token stored in environment variables.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from starlette.routing import Route

# Load configuration from .env
load_dotenv()

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_USER_TOKEN = os.getenv('SLACK_USER_TOKEN')
SLACK_SAFE_SEARCH = os.getenv('SLACK_SAFE_SEARCH', 'false').lower() == 'true'

# Initialize FastMCP server
mcp = FastMCP("SlackMCP")

# Initialize Slack clients
bot_client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None
user_client = WebClient(token=SLACK_USER_TOKEN) if SLACK_USER_TOKEN else None


@mcp.tool()
async def slack_list_channels(limit: int = 100) -> Dict[str, Any]:
    """
    List all channels the bot has access to.

    Args:
        limit (int): Maximum number of channels to return. Defaults to 100.

    Returns:
        Dict containing success status and channel list or error message.
    """
    try:
        if not bot_client:
            return {"success": False, "error": "Slack bot token not configured"}

        result = bot_client.conversations_list(limit=limit)
        channels = []

        for channel in result["channels"]:
            channels.append({
                "id": channel["id"],
                "name": channel["name"],
                "is_channel": channel["is_channel"],
                "is_group": channel["is_group"],
                "is_im": channel["is_im"],
                "created": channel["created"],
                "creator": channel["creator"],
                "members": channel.get("members", []),
                "topic": channel.get("topic", {}).get("value", ""),
                "purpose": channel.get("purpose", {}).get("value", "")
            })

        return {
            "success": True,
            "channels": channels,
            "total_count": len(channels)
        }

    except SlackApiError as e:
        return {"success": False, "error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def slack_get_channel_history(channel_name: str, limit: int = 50) -> Dict[str, Any]:
    """
    Get recent messages from a Slack channel.

    Args:
        channel_name (str): Name of the channel (without #) or channel ID
        limit (int): Maximum number of messages to return. Defaults to 50.

    Returns:
        Dict containing success status and message list or error message.
    """
    try:
        if not bot_client:
            return {"success": False, "error": "Slack bot token not configured"}

        # First, find the channel ID if a name was provided
        if not channel_name.startswith(('C', 'G', 'D')):
            # It's a channel name, find the ID
            result = bot_client.conversations_list()
            channel_id = None
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    channel_id = channel["id"]
                    break

            if not channel_id:
                return {"success": False, "error": f"Channel '{channel_name}' not found"}
        else:
            channel_id = channel_name

        # Get channel history
        result = bot_client.conversations_history(channel=channel_id, limit=limit)

        messages = []
        for message in result["messages"]:
            messages.append({
                "ts": message["ts"],
                "user": message.get("user", ""),
                "text": message.get("text", ""),
                "timestamp": datetime.fromtimestamp(float(message["ts"])).isoformat(),
                "thread_ts": message.get("thread_ts"),
                "reply_count": message.get("reply_count", 0),
                "reactions": message.get("reactions", [])
            })

        return {
            "success": True,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "messages": messages,
            "total_count": len(messages)
        }

    except SlackApiError as e:
        return {"success": False, "error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def slack_post_message(channel_name: str, text: str) -> Dict[str, Any]:
    """
    Post a message to a Slack channel.

    Args:
        channel_name (str): Name of the channel (without #) or channel ID
        text (str): Message text to post

    Returns:
        Dict containing success status and message details or error message.
    """
    try:
        if not bot_client:
            return {"success": False, "error": "Slack bot token not configured"}

        # Find channel ID if name provided
        if not channel_name.startswith(('C', 'G', 'D')):
            result = bot_client.conversations_list()
            channel_id = None
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    channel_id = channel["id"]
                    break

            if not channel_id:
                return {"success": False, "error": f"Channel '{channel_name}' not found"}
        else:
            channel_id = channel_name

        # Post message
        result = bot_client.chat_postMessage(channel=channel_id, text=text)

        return {
            "success": True,
            "channel": result["channel"],
            "ts": result["ts"],
            "message": {
                "text": text,
                "timestamp": datetime.fromtimestamp(float(result["ts"])).isoformat()
            }
        }

    except SlackApiError as e:
        return {"success": False, "error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def slack_reply_to_thread(channel_name: str, thread_ts: str, text: str) -> Dict[str, Any]:
    """
    Reply to a message thread in Slack.

    Args:
        channel_name (str): Name of the channel (without #) or channel ID
        thread_ts (str): Timestamp of the parent message to reply to
        text (str): Reply text

    Returns:
        Dict containing success status and reply details or error message.
    """
    try:
        if not bot_client:
            return {"success": False, "error": "Slack bot token not configured"}

        # Find channel ID if name provided
        if not channel_name.startswith(('C', 'G', 'D')):
            result = bot_client.conversations_list()
            channel_id = None
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    channel_id = channel["id"]
                    break

            if not channel_id:
                return {"success": False, "error": f"Channel '{channel_name}' not found"}
        else:
            channel_id = channel_name

        # Post reply to thread
        result = bot_client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts
        )

        return {
            "success": True,
            "channel": result["channel"],
            "ts": result["ts"],
            "thread_ts": thread_ts,
            "message": {
                "text": text,
                "timestamp": datetime.fromtimestamp(float(result["ts"])).isoformat()
            }
        }

    except SlackApiError as e:
        return {"success": False, "error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def slack_add_reaction(channel_name: str, timestamp: str, reaction: str) -> Dict[str, Any]:
    """
    Add an emoji reaction to a Slack message.

    Args:
        channel_name (str): Name of the channel (without #) or channel ID
        timestamp (str): Timestamp of the message to react to
        reaction (str): Emoji name without colons (e.g., "thumbsup", "heart")

    Returns:
        Dict containing success status or error message.
    """
    try:
        if not bot_client:
            return {"success": False, "error": "Slack bot token not configured"}

        # Find channel ID if name provided
        if not channel_name.startswith(('C', 'G', 'D')):
            result = bot_client.conversations_list()
            channel_id = None
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    channel_id = channel["id"]
                    break

            if not channel_id:
                return {"success": False, "error": f"Channel '{channel_name}' not found"}
        else:
            channel_id = channel_name

        # Add reaction
        bot_client.reactions_add(
            channel=channel_id,
            timestamp=timestamp,
            name=reaction
        )

        return {
            "success": True,
            "channel": channel_id,
            "timestamp": timestamp,
            "reaction": reaction
        }

    except SlackApiError as e:
        return {"success": False, "error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def slack_get_thread_replies(channel_name: str, thread_ts: str) -> Dict[str, Any]:
    """
    Get all replies in a Slack message thread.

    Args:
        channel_name (str): Name of the channel (without #) or channel ID
        thread_ts (str): Timestamp of the parent message

    Returns:
        Dict containing success status and thread replies or error message.
    """
    try:
        if not bot_client:
            return {"success": False, "error": "Slack bot token not configured"}

        # Find channel ID if name provided
        if not channel_name.startswith(('C', 'G', 'D')):
            result = bot_client.conversations_list()
            channel_id = None
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    channel_id = channel["id"]
                    break

            if not channel_id:
                return {"success": False, "error": f"Channel '{channel_name}' not found"}
        else:
            channel_id = channel_name

        # Get thread replies
        result = bot_client.conversations_replies(channel=channel_id, ts=thread_ts)

        replies = []
        for message in result["messages"]:
            replies.append({
                "ts": message["ts"],
                "user": message.get("user", ""),
                "text": message.get("text", ""),
                "timestamp": datetime.fromtimestamp(float(message["ts"])).isoformat(),
                "thread_ts": message.get("thread_ts"),
                "reactions": message.get("reactions", [])
            })

        return {
            "success": True,
            "channel_id": channel_id,
            "thread_ts": thread_ts,
            "replies": replies,
            "total_count": len(replies)
        }

    except SlackApiError as e:
        return {"success": False, "error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def slack_search_messages(query: str, limit: int = 20) -> Dict[str, Any]:
    """
    Search for messages in Slack using the user token (requires search:read scope).

    Args:
        query (str): Search query (supports Slack search syntax)
        limit (int): Maximum number of results to return. Defaults to 20.

    Returns:
        Dict containing success status and search results or error message.
    """
    try:
        if not user_client:
            return {"success": False, "error": "Slack user token not configured"}

        # Perform search
        result = user_client.search_messages(query=query, count=limit)

        messages = []
        if "messages" in result and "matches" in result["messages"]:
            for match in result["messages"]["matches"]:
                messages.append({
                    "ts": match["ts"],
                    "text": match.get("text", ""),
                    "user": match.get("user", ""),
                    "channel": match.get("channel", {}),
                    "timestamp": datetime.fromtimestamp(float(match["ts"])).isoformat(),
                    "permalink": match.get("permalink", "")
                })

        return {
            "success": True,
            "query": query,
            "messages": messages,
            "total_count": len(messages)
        }

    except SlackApiError as e:
        return {"success": False, "error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def slack_get_users(limit: int = 100) -> Dict[str, Any]:
    """
    Get list of users in the Slack workspace.

    Args:
        limit (int): Maximum number of users to return. Defaults to 100.

    Returns:
        Dict containing success status and user list or error message.
    """
    try:
        if not bot_client:
            return {"success": False, "error": "Slack bot token not configured"}

        result = bot_client.users_list(limit=limit)

        users = []
        for user in result["members"]:
            if not user.get("is_bot", False) and not user.get("deleted", False):
                users.append({
                    "id": user["id"],
                    "name": user["name"],
                    "real_name": user.get("real_name", ""),
                    "display_name": user.get("profile", {}).get("display_name", ""),
                    "email": user.get("profile", {}).get("email", ""),
                    "tz": user.get("tz", ""),
                    "is_admin": user.get("is_admin", False),
                    "is_owner": user.get("is_owner", False)
                })

        return {
            "success": True,
            "users": users,
            "total_count": len(users)
        }

    except SlackApiError as e:
        return {"success": False, "error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def slack_search_users(query: str) -> Dict[str, Any]:
    """
    Search for users in the Slack workspace.

    Args:
        query (str): Search query for finding users

    Returns:
        Dict containing success status and user search results or error message.
    """
    try:
        if not bot_client:
            return {"success": False, "error": "Slack bot token not configured"}

        result = bot_client.users_list()

        matching_users = []
        query_lower = query.lower()

        for user in result["members"]:
            if not user.get("is_bot", False) and not user.get("deleted", False):
                # Search in name, real_name, and email
                searchable_text = f"{user['name']} {user.get('real_name', '')} {user.get('profile', {}).get('email', '')}".lower()

                if query_lower in searchable_text:
                    matching_users.append({
                        "id": user["id"],
                        "name": user["name"],
                        "real_name": user.get("real_name", ""),
                        "display_name": user.get("profile", {}).get("display_name", ""),
                        "email": user.get("profile", {}).get("email", ""),
                        "tz": user.get("tz", "")
                    })

        return {
            "success": True,
            "query": query,
            "users": matching_users,
            "total_count": len(matching_users)
        }

    except SlackApiError as e:
        return {"success": False, "error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def slack_search_channels(query: str) -> Dict[str, Any]:
    """
    Search for channels in the Slack workspace.

    Args:
        query (str): Search query for finding channels

    Returns:
        Dict containing success status and channel search results or error message.
    """
    try:
        if not bot_client:
            return {"success": False, "error": "Slack bot token not configured"}

        result = bot_client.conversations_list()

        matching_channels = []
        query_lower = query.lower()

        for channel in result["channels"]:
            if query_lower in channel["name"].lower():
                matching_channels.append({
                    "id": channel["id"],
                    "name": channel["name"],
                    "is_channel": channel["is_channel"],
                    "is_group": channel["is_group"],
                    "is_im": channel["is_im"],
                    "created": channel["created"],
                    "creator": channel["creator"],
                    "members": channel.get("members", []),
                    "topic": channel.get("topic", {}).get("value", ""),
                    "purpose": channel.get("purpose", {}).get("value", "")
                })

        return {
            "success": True,
            "query": query,
            "channels": matching_channels,
            "total_count": len(matching_channels)
        }

    except SlackApiError as e:
        return {"success": False, "error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


async def health_check(request):
    """Health check endpoint for Kubernetes liveness and readiness probes."""
    try:
        # Basic health check - verify required environment variables exist
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        user_token = os.getenv("SLACK_USER_TOKEN")

        if not bot_token or not user_token:
            return JSONResponse({
                "status": "unhealthy",
                "error": "Missing required Slack tokens",
                "missing_tokens": [
                    "SLACK_BOT_TOKEN" if not bot_token else None,
                    "SLACK_USER_TOKEN" if not user_token else None
                ]
            }, status_code=503)

        # Check if tokens look valid (basic format check)
        if not bot_token.startswith('xoxb-') and not bot_token.startswith('xapp-'):
            return JSONResponse({
                "status": "unhealthy",
                "error": "Invalid SLACK_BOT_TOKEN format"
            }, status_code=503)

        if not user_token.startswith('xoxp-'):
            return JSONResponse({
                "status": "unhealthy",
                "error": "Invalid SLACK_USER_TOKEN format"
            }, status_code=503)

        return JSONResponse({
            "status": "healthy",
            "service": "Slack MCP Server",
            "version": "0.1.5",
            "transport": "sse",
            "sse_endpoint": "/sse",
            "tools_available": 9,
            "has_valid_tokens": True
        })

    except Exception as e:
        return JSONResponse({"status": "unhealthy", "error": str(e)}, status_code=503)


def main():
    """Main entry point for the Slack MCP server."""
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="Slack MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")

    args = parser.parse_args()

    # Get the SSE app from FastMCP
    app = mcp.sse_app()

    # Add health check endpoint
    app.routes.append(Route("/health", health_check))

    # Run the server with HTTP streaming
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
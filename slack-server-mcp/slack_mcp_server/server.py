"""Slack MCP Server - FastMCP implementation."""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
import click
import uvicorn
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from fastmcp import FastMCP
from .schemas import (
    AddReactionRequest,
    ConversationsHistoryResponse, 
    ConversationsRepliesResponse,
    GetChannelHistoryRequest,
    GetThreadRepliesRequest,
    GetUserProfilesRequest,
    GetUsersRequest,
    ListChannelsRequest,
    ListChannelsResponse,
    PostMessageRequest,
    ReplyToThreadRequest,
    SearchChannelsRequest,
    SearchMessagesRequest,
    SearchUsersRequest,
    GetUsersResponse,
    GetUserProfilesResponse,
    SearchMessagesResponse,
)

# Load environment variables
load_dotenv()

# Validate required environment variables
if not os.getenv("SLACK_BOT_TOKEN"):
    print("SLACK_BOT_TOKEN is not set. Please set it in your environment or .env file.")
    sys.exit(1)

if not os.getenv("SLACK_USER_TOKEN"):
    print("SLACK_USER_TOKEN is not set. Please set it in your environment or .env file.")
    sys.exit(1)

# Initialize Slack clients
slack_client = AsyncWebClient(token=os.getenv("SLACK_BOT_TOKEN"))
user_client = AsyncWebClient(token=os.getenv("SLACK_USER_TOKEN"))

# Safe search mode configuration
safe_search_mode = os.getenv("SLACK_SAFE_SEARCH", "false").lower() == "true"
if safe_search_mode:
    print("Safe search mode enabled: Private channels and DMs will be excluded from search results")

# Initialize FastMCP
mcp = FastMCP("Slack MCP Server")

# Add health endpoint for Kubernetes probes
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route

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
            "tools_available": 11,
            "has_valid_tokens": True
        })
    except Exception as e:
        return JSONResponse({"status": "unhealthy", "error": str(e)}, status_code=503)


@mcp.tool()
async def slack_list_channels(request: ListChannelsRequest) -> str:
    """List public channels in the workspace with pagination."""
    try:
        response = await slack_client.conversations_list(
            limit=request.limit,
            cursor=request.cursor,
            types="public_channel"  # Only public channels
        )
        
        if not response["ok"]:
            raise Exception(f"Failed to list channels: {response.get('error', 'Unknown error')}")
        
        # Parse response using Pydantic model
        parsed_response = ListChannelsResponse(**response.data)
        return json.dumps(parsed_response.model_dump(), indent=2)
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error listing channels: {str(e)}")


@mcp.tool()
async def slack_post_message(request: PostMessageRequest) -> str:
    """Post a new message to a Slack channel."""
    try:
        response = await slack_client.chat_postMessage(
            channel=request.channel_id,
            text=request.text
        )
        
        if not response["ok"]:
            raise Exception(f"Failed to post message: {response.get('error', 'Unknown error')}")
        
        return "Message posted successfully"
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error posting message: {str(e)}")


@mcp.tool()
async def slack_reply_to_thread(request: ReplyToThreadRequest) -> str:
    """Reply to a specific message thread in Slack."""
    try:
        response = await slack_client.chat_postMessage(
            channel=request.channel_id,
            thread_ts=request.thread_ts,
            text=request.text
        )
        
        if not response["ok"]:
            raise Exception(f"Failed to reply to thread: {response.get('error', 'Unknown error')}")
        
        return "Reply sent to thread successfully"
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error replying to thread: {str(e)}")


@mcp.tool()
async def slack_add_reaction(request: AddReactionRequest) -> str:
    """Add a reaction emoji to a message."""
    try:
        response = await slack_client.reactions_add(
            channel=request.channel_id,
            timestamp=request.timestamp,
            name=request.reaction
        )
        
        if not response["ok"]:
            raise Exception(f"Failed to add reaction: {response.get('error', 'Unknown error')}")
        
        return "Reaction added successfully"
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error adding reaction: {str(e)}")


@mcp.tool()
async def slack_get_channel_history(request: GetChannelHistoryRequest) -> str:
    """Get messages from a channel in chronological order. Use this when: 1) You need the latest conversation flow without specific filters, 2) You want ALL messages including bot/automation messages, 3) You need to browse messages sequentially with pagination. Do NOT use if you have specific search criteria (user, keywords, dates) - use slack_search_messages instead."""
    try:
        response = await slack_client.conversations_history(
            channel=request.channel_id,
            limit=request.limit,
            cursor=request.cursor
        )
        
        if not response["ok"]:
            raise Exception(f"Failed to get channel history: {response.get('error', 'Unknown error')}")
        
        # Parse response using Pydantic model
        parsed_response = ConversationsHistoryResponse(**response.data)
        return json.dumps(parsed_response.model_dump(), indent=2)
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error getting channel history: {str(e)}")


@mcp.tool()
async def slack_get_thread_replies(request: GetThreadRepliesRequest) -> str:
    """Get all replies in a message thread."""
    try:
        response = await slack_client.conversations_replies(
            channel=request.channel_id,
            ts=request.thread_ts,
            limit=request.limit,
            cursor=request.cursor
        )
        
        if not response["ok"]:
            raise Exception(f"Failed to get thread replies: {response.get('error', 'Unknown error')}")
        
        # Parse response using Pydantic model
        parsed_response = ConversationsRepliesResponse(**response.data)
        return json.dumps(parsed_response.model_dump(), indent=2)
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error getting thread replies: {str(e)}")


@mcp.tool()
async def slack_get_users(request: GetUsersRequest) -> str:
    """Retrieve basic profile information of all users in the workspace."""
    try:
        response = await slack_client.users_list(
            limit=request.limit,
            cursor=request.cursor
        )
        
        if not response["ok"]:
            raise Exception(f"Failed to get users: {response.get('error', 'Unknown error')}")
        
        # Parse response using Pydantic model
        parsed_response = GetUsersResponse(**response.data)
        return json.dumps(parsed_response.model_dump(), indent=2)
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error getting users: {str(e)}")


@mcp.tool()
async def slack_get_user_profiles(request: GetUserProfilesRequest) -> str:
    """Get multiple users profile information in bulk."""
    try:
        profiles = []
        
        for user_id in request.user_ids:
            response = await slack_client.users_profile_get(user=user_id)
            profiles.append(response.data)
        
        # Create response structure
        profiles_response = GetUserProfilesResponse(profiles=profiles)
        return json.dumps(profiles_response.model_dump(), indent=2)
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error getting user profiles: {str(e)}")


@mcp.tool()
async def slack_search_messages(request: SearchMessagesRequest) -> str:
    """Search for messages with specific criteria/filters. Use this when: 1) You need to find messages from a specific user, 2) You need messages from a specific date range, 3) You need to search by keywords, 4) You want to filter by channel. This tool is optimized for targeted searches. For general channel browsing without filters, use slack_get_channel_history instead."""
    try:
        # Use user client for search (requires user token)
        response = await user_client.search_messages(
            query=request.query,
            sort=request.sort,
            sort_dir=request.sort_dir,
            highlight=request.highlight,
            count=request.count,
            page=request.page
        )
        
        if not response["ok"]:
            raise Exception(f"Failed to search messages: {response.get('error', 'Unknown error')}")
        
        # Filter out private channels and DMs if safe search mode is enabled
        if safe_search_mode and "messages" in response.data:
            filtered_matches = []
            for match in response.data["messages"].get("matches", []):
                channel = match.get("channel", {})
                # Skip private channels and DMs
                if not channel.get("is_private", True) and not channel.get("is_im", False):
                    filtered_matches.append(match)
            
            response.data["messages"]["matches"] = filtered_matches
            response.data["messages"]["total"] = len(filtered_matches)
        
        # Parse response using Pydantic model
        parsed_response = SearchMessagesResponse(**response.data)
        return json.dumps(parsed_response.model_dump(), indent=2)
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error searching messages: {str(e)}")


@mcp.tool()
async def slack_search_channels(request: SearchChannelsRequest) -> str:
    """Search for channels by partial name match. Use this when you need to find channels containing specific keywords in their names. Returns up to the specified limit of matching channels."""
    try:
        # Get all channels first
        all_channels = []
        cursor = None
        
        while True:
            response = await slack_client.conversations_list(
                limit=1000,
                cursor=cursor,
                types="public_channel"
            )
            
            if not response["ok"]:
                raise Exception(f"Failed to list channels: {response.get('error', 'Unknown error')}")
            
            all_channels.extend(response.data.get("channels", []))
            
            if not response.data.get("response_metadata", {}).get("next_cursor"):
                break
            cursor = response.data["response_metadata"]["next_cursor"]
        
        # Filter channels by query
        matching_channels = []
        query_lower = request.query.lower()
        
        for channel in all_channels:
            channel_name = channel.get("name", "").lower()
            if query_lower in channel_name:
                matching_channels.append(channel)
                if len(matching_channels) >= request.limit:
                    break
        
        result = {
            "ok": True,
            "channels": matching_channels,
            "total": len(matching_channels)
        }
        
        return json.dumps(result, indent=2)
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error searching channels: {str(e)}")


@mcp.tool()
async def slack_search_users(request: SearchUsersRequest) -> str:
    """Search for users by partial name match across username, display name, and real name. Use this when you need to find users containing specific keywords in their names. Returns up to the specified limit of matching users."""
    try:
        # Get all users first
        all_users = []
        cursor = None
        
        while True:
            response = await slack_client.users_list(
                limit=1000,
                cursor=cursor
            )
            
            if not response["ok"]:
                raise Exception(f"Failed to list users: {response.get('error', 'Unknown error')}")
            
            all_users.extend(response.data.get("members", []))
            
            if not response.data.get("response_metadata", {}).get("next_cursor"):
                break
            cursor = response.data["response_metadata"]["next_cursor"]
        
        # Filter users by query
        matching_users = []
        query_lower = request.query.lower()
        
        for user in all_users:
            # Skip deleted users and bots
            if user.get("deleted", False) or user.get("is_bot", False):
                continue
                
            # Search in various name fields
            searchable_fields = [
                user.get("name", ""),
                user.get("real_name", ""),
                user.get("profile", {}).get("display_name", ""),
                user.get("profile", {}).get("real_name", ""),
            ]
            
            if any(query_lower in field.lower() for field in searchable_fields if field):
                matching_users.append(user)
                if len(matching_users) >= request.limit:
                    break
        
        result = {
            "ok": True,
            "members": matching_users,
            "total": len(matching_users)
        }
        
        return json.dumps(result, indent=2)
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise Exception(f"Error searching users: {str(e)}")


@click.command()
@click.option("--port", type=int, help="Start the server with SSE transport on the specified port")
@click.option("--help", is_flag=True, help="Show this help message")
def main(port: Optional[int] = None, help: bool = False) -> None:
    """Slack MCP Server - FastMCP implementation."""
    
    if help:
        print("""
Usage: slack-mcp-server [options]

Options:
  --port <number>    Start the server with SSE transport on the specified port
  --help             Show this help message

Examples:
  slack-mcp-server                  # Start with stdio transport (default)
  slack-mcp-server --port 8000      # Start with SSE transport on port 8000
        """)
        return
    
    if port:
        # SSE server mode
        print(f"Starting Slack MCP Server with SSE transport on port {port}")
        print(f"SSE endpoint available at: http://0.0.0.0:{port}/sse")
        
        # Use FastMCP's built-in SSE async runner
        async def run_server():
            # Add health endpoint to the SSE app
            app = mcp.sse_app()
            app.routes.append(Route("/health", health_check))
            
            # Run the SSE server
            config = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
        
        # Run the async server
        asyncio.run(run_server())
    else:
        # STDIO mode (default)
        print("Starting Slack MCP Server in STDIO mode", file=sys.stderr)
        mcp.run()


if __name__ == "__main__":
    main()
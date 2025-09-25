"""Main MCP server implementation for Microsoft Teams."""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from mcp_teams.teams.client import TeamsClient
from mcp_teams.utils.env import is_env_truthy

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Microsoft Teams MCP Server")

# Configure FastMCP settings
settings = mcp.settings
settings.sse_path = "/sse"
settings.streamable_http_path = "/mcp"

# Global client instance
_teams_client: Optional[TeamsClient] = None


def get_teams_client() -> TeamsClient:
    """Get or create Teams client instance."""
    global _teams_client
    
    if _teams_client is None:
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        tenant_id = os.getenv("AZURE_TENANT_ID")
        
        if not all([client_id, client_secret, tenant_id]):
            raise ValueError(
                "Missing required environment variables: "
                "AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID"
            )
        
        _teams_client = TeamsClient(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
        )
    
    return _teams_client


def is_read_only() -> bool:
    """Check if server is running in read-only mode."""
    return is_env_truthy("READ_ONLY_MODE", "false")


# Tool input models
class SendMessageInput(BaseModel):
    team_id: Optional[str] = Field(default=None, description="Team ID (for channel messages)")
    channel_id: Optional[str] = Field(default=None, description="Channel ID (for channel messages)")
    chat_id: Optional[str] = Field(default=None, description="Chat ID (for chat messages)")
    content: str = Field(description="Message content")
    content_type: str = Field(default="html", description="Content type (html or text)")


class GetMessagesInput(BaseModel):
    team_id: Optional[str] = Field(default=None, description="Team ID (for channel messages)")
    channel_id: Optional[str] = Field(default=None, description="Channel ID (for channel messages)")
    chat_id: Optional[str] = Field(default=None, description="Chat ID (for chat messages)")
    limit: int = Field(default=50, description="Maximum number of messages")


class SearchMessagesInput(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=25, description="Maximum number of results")


class GetTeamChannelsInput(BaseModel):
    team_id: str = Field(description="Team ID")


class CreateChannelInput(BaseModel):
    team_id: str = Field(description="Team ID")
    display_name: str = Field(description="Channel display name")
    description: Optional[str] = Field(default=None, description="Channel description")


class CreateMeetingInput(BaseModel):
    subject: str = Field(description="Meeting subject")
    start_time: str = Field(description="Start time (ISO format)")
    end_time: str = Field(description="End time (ISO format)")
    attendees: Optional[List[str]] = Field(default=None, description="List of attendee email addresses")


class GetChannelFilesInput(BaseModel):
    team_id: str = Field(description="Team ID")
    channel_id: str = Field(description="Channel ID")


# Teams tools
@mcp.tool()
async def teams_get_my_teams() -> Dict[str, Any]:
    """Get teams the current user is a member of."""
    try:
        client = get_teams_client()
        teams = await client.get_my_teams()
        return {
            "teams": [team.model_dump() for team in teams],
            "count": len(teams)
        }
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        return {"error": str(e)}


@mcp.tool()
async def teams_get_team_channels(input_data: GetTeamChannelsInput) -> Dict[str, Any]:
    """Get channels in a team."""
    try:
        client = get_teams_client()
        channels = await client.get_team_channels(input_data.team_id)
        return {
            "team_id": input_data.team_id,
            "channels": [channel.model_dump() for channel in channels],
            "count": len(channels)
        }
    except Exception as e:
        logger.error(f"Error getting team channels: {e}")
        return {"error": str(e)}


@mcp.tool()
async def teams_get_messages(input_data: GetMessagesInput) -> Dict[str, Any]:
    """Get messages from a channel or chat."""
    try:
        client = get_teams_client()
        
        if input_data.team_id and input_data.channel_id:
            messages = await client.get_channel_messages(
                input_data.team_id, 
                input_data.channel_id, 
                input_data.limit
            )
            context = f"team {input_data.team_id}, channel {input_data.channel_id}"
        elif input_data.chat_id:
            messages = await client.get_chat_messages(input_data.chat_id, input_data.limit)
            context = f"chat {input_data.chat_id}"
        else:
            return {"error": "Either (team_id and channel_id) or chat_id must be provided"}
        
        return {
            "context": context,
            "messages": [message.model_dump() for message in messages],
            "count": len(messages)
        }
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return {"error": str(e)}


@mcp.tool()
async def teams_send_message(input_data: SendMessageInput) -> Dict[str, Any]:
    """Send a message to a Teams channel or chat."""
    if is_read_only():
        return {"error": "Server is running in read-only mode"}
    
    try:
        client = get_teams_client()
        
        if input_data.team_id and input_data.channel_id:
            message = await client.send_channel_message(
                input_data.team_id,
                input_data.channel_id,
                input_data.content,
                input_data.content_type
            )
            context = f"team {input_data.team_id}, channel {input_data.channel_id}"
        elif input_data.chat_id:
            message = await client.send_chat_message(
                input_data.chat_id,
                input_data.content,
                input_data.content_type
            )
            context = f"chat {input_data.chat_id}"
        else:
            return {"error": "Either (team_id and channel_id) or chat_id must be provided"}
        
        return {
            "message": "Message sent successfully",
            "context": context,
            "sent_message": message.model_dump()
        }
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {"error": str(e)}


@mcp.tool()
async def teams_search_messages(input_data: SearchMessagesInput) -> Dict[str, Any]:
    """Search for messages across Teams."""
    try:
        client = get_teams_client()
        results = await client.search_messages(input_data.query, input_data.limit)
        return {
            "query": input_data.query,
            "results": [result.model_dump() for result in results],
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        return {"error": str(e)}


@mcp.tool()
async def teams_get_my_chats() -> Dict[str, Any]:
    """Get the current user's chats."""
    try:
        client = get_teams_client()
        chats = await client.get_my_chats()
        return {
            "chats": [chat.model_dump() for chat in chats],
            "count": len(chats)
        }
    except Exception as e:
        logger.error(f"Error getting chats: {e}")
        return {"error": str(e)}


@mcp.tool()
async def teams_create_channel(input_data: CreateChannelInput) -> Dict[str, Any]:
    """Create a new channel in a team."""
    if is_read_only():
        return {"error": "Server is running in read-only mode"}
    
    try:
        client = get_teams_client()
        channel = await client.create_channel(
            input_data.team_id,
            input_data.display_name,
            input_data.description
        )
        
        return {
            "message": "Channel created successfully",
            "channel": channel.model_dump()
        }
    except Exception as e:
        logger.error(f"Error creating channel: {e}")
        return {"error": str(e)}


@mcp.tool()
async def teams_create_meeting(input_data: CreateMeetingInput) -> Dict[str, Any]:
    """Create a Teams meeting."""
    if is_read_only():
        return {"error": "Server is running in read-only mode"}
    
    try:
        client = get_teams_client()
        
        # Parse datetime strings
        start_time = datetime.fromisoformat(input_data.start_time.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(input_data.end_time.replace('Z', '+00:00'))
        
        meeting = await client.create_meeting(
            input_data.subject,
            start_time,
            end_time,
            input_data.attendees
        )
        
        return {
            "message": "Meeting created successfully",
            "meeting": meeting.model_dump()
        }
    except Exception as e:
        logger.error(f"Error creating meeting: {e}")
        return {"error": str(e)}


@mcp.tool()
async def teams_get_my_meetings() -> Dict[str, Any]:
    """Get the current user's upcoming meetings."""
    try:
        client = get_teams_client()
        meetings = await client.get_my_meetings()
        return {
            "meetings": [meeting.model_dump() for meeting in meetings],
            "count": len(meetings)
        }
    except Exception as e:
        logger.error(f"Error getting meetings: {e}")
        return {"error": str(e)}


@mcp.tool()
async def teams_get_channel_files(input_data: GetChannelFilesInput) -> Dict[str, Any]:
    """Get files in a Teams channel."""
    try:
        client = get_teams_client()
        files = await client.get_channel_files(input_data.team_id, input_data.channel_id)
        return {
            "team_id": input_data.team_id,
            "channel_id": input_data.channel_id,
            "files": [file.model_dump() for file in files],
            "count": len(files)
        }
    except Exception as e:
        logger.error(f"Error getting channel files: {e}")
        return {"error": str(e)}


# Export the FastMCP instance
__all__ = ["mcp"]
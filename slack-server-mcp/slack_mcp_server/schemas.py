"""Pydantic schemas for Slack MCP Server."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import re


class Channel(BaseModel):
    """Slack channel information."""
    
    conversation_host_id: Optional[str] = None
    created: Optional[int] = None
    id: Optional[str] = None
    is_archived: Optional[bool] = None
    name: Optional[str] = None
    name_normalized: Optional[str] = None
    num_members: Optional[int] = None
    purpose: Optional[Dict[str, Any]] = None
    shared_team_ids: Optional[List[str]] = None
    topic: Optional[Dict[str, Any]] = None
    updated: Optional[int] = None


class Reaction(BaseModel):
    """Slack reaction information."""
    
    count: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None
    users: Optional[List[str]] = None


class Message(BaseModel):
    """Slack message information."""
    
    reactions: Optional[List[Reaction]] = None
    reply_count: Optional[int] = None
    reply_users: Optional[List[str]] = None
    reply_users_count: Optional[int] = None
    subtype: Optional[str] = None
    text: Optional[str] = None
    thread_ts: Optional[str] = None
    ts: Optional[str] = None
    type: Optional[str] = None
    user: Optional[str] = None


class Member(BaseModel):
    """Slack member information."""
    
    id: Optional[str] = None
    name: Optional[str] = None
    real_name: Optional[str] = None


class Profile(BaseModel):
    """Slack user profile information."""
    
    display_name: Optional[str] = None
    display_name_normalized: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    real_name_normalized: Optional[str] = None
    title: Optional[str] = None


class SearchMessage(BaseModel):
    """Slack search message result."""
    
    channel: Optional[Dict[str, str]] = None
    permalink: Optional[str] = None
    text: Optional[str] = None
    ts: Optional[str] = None
    type: Optional[str] = None
    user: Optional[str] = None


# Request schemas
class ListChannelsRequest(BaseModel):
    """Request schema for listing channels."""
    
    cursor: Optional[str] = Field(
        None, 
        description="Pagination cursor for next page of results"
    )
    limit: Optional[int] = Field(
        100,
        ge=1,
        le=1000,
        description="Maximum number of channels to return (default 100)"
    )


class PostMessageRequest(BaseModel):
    """Request schema for posting a message."""
    
    channel_id: str = Field(description="The ID of the channel to post to")
    text: str = Field(description="The message text to post")


class ReplyToThreadRequest(BaseModel):
    """Request schema for replying to a thread."""
    
    channel_id: str = Field(description="The ID of the channel containing the thread")
    thread_ts: str = Field(
        description="The timestamp of the parent message in the format '1234567890.123456'"
    )
    text: str = Field(description="The reply text")


class AddReactionRequest(BaseModel):
    """Request schema for adding a reaction."""
    
    channel_id: str = Field(description="The ID of the channel containing the message")
    reaction: str = Field(description="The name of the emoji reaction (without ::)")
    timestamp: str = Field(
        description="The timestamp of the message to react to in the format '1234567890.123456'"
    )

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        if not re.match(r'^\d{10}\.\d{6}$', v):
            raise ValueError("Timestamp must be in the format '1234567890.123456'")
        return v


class GetChannelHistoryRequest(BaseModel):
    """Request schema for getting channel history."""
    
    channel_id: str = Field(
        description="The ID of the channel. Use this tool for: browsing latest messages without filters, getting ALL messages including bot/automation messages, sequential pagination. If you need to search by user, keywords, or dates, use slack_search_messages instead."
    )
    cursor: Optional[str] = Field(
        None,
        description="Pagination cursor for next page of results"
    )
    limit: Optional[int] = Field(
        100,
        ge=1,
        le=1000,
        description="Number of messages to retrieve (default 100)"
    )


class GetThreadRepliesRequest(BaseModel):
    """Request schema for getting thread replies."""
    
    channel_id: str = Field(description="The ID of the channel containing the thread")
    thread_ts: str = Field(
        description="The timestamp of the parent message in the format '1234567890.123456'. Timestamps in the format without the period can be converted by adding the period such that 6 numbers come after it."
    )
    cursor: Optional[str] = Field(
        None,
        description="Pagination cursor for next page of results"
    )
    limit: Optional[int] = Field(
        100,
        ge=1,
        le=1000,
        description="Number of replies to retrieve (default 100)"
    )

    @field_validator('thread_ts')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        if not re.match(r'^\d{10}\.\d{6}$', v):
            raise ValueError("Timestamp must be in the format '1234567890.123456'")
        return v


class GetUsersRequest(BaseModel):
    """Request schema for getting users."""
    
    cursor: Optional[str] = Field(
        None,
        description="Pagination cursor for next page of results"
    )
    limit: Optional[int] = Field(
        100,
        ge=1,
        description="Maximum number of users to return (default 100)"
    )


class GetUserProfilesRequest(BaseModel):
    """Request schema for getting user profiles."""
    
    user_ids: List[str] = Field(
        description="Array of user IDs to retrieve profiles for (max 100)",
        min_length=1,
        max_length=100
    )


class SearchMessagesRequest(BaseModel):
    """Request schema for searching messages."""
    
    query: str = Field(description="Search query string")
    sort: Optional[str] = Field("timestamp", description="Sort order (timestamp or score)")
    sort_dir: Optional[str] = Field("desc", description="Sort direction (asc or desc)")
    highlight: Optional[bool] = Field(False, description="Enable search result highlighting")
    count: Optional[int] = Field(
        20,
        ge=1,
        le=1000,
        description="Number of items to return per page (default 20)"
    )
    page: Optional[int] = Field(
        1,
        ge=1,
        description="Page number of results to return (default 1)"
    )


class SearchChannelsRequest(BaseModel):
    """Request schema for searching channels."""
    
    query: str = Field(description="Channel name search query")
    limit: Optional[int] = Field(
        20,
        ge=1,
        le=1000,
        description="Maximum number of channels to return (default 20)"
    )


class SearchUsersRequest(BaseModel):
    """Request schema for searching users."""
    
    query: str = Field(description="User name search query")
    limit: Optional[int] = Field(
        20,
        ge=1,
        le=1000,
        description="Maximum number of users to return (default 20)"
    )


# Response schemas
class ListChannelsResponse(BaseModel):
    """Response schema for listing channels."""
    
    ok: bool
    channels: Optional[List[Channel]] = None
    response_metadata: Optional[Dict[str, Any]] = None


class GetUsersResponse(BaseModel):
    """Response schema for getting users."""
    
    ok: bool
    members: Optional[List[Member]] = None
    response_metadata: Optional[Dict[str, Any]] = None


class UserProfileResponse(BaseModel):
    """Response schema for user profile."""
    
    ok: bool
    profile: Optional[Profile] = None


class GetUserProfilesResponse(BaseModel):
    """Response schema for getting user profiles."""
    
    profiles: List[UserProfileResponse]


class ConversationsHistoryResponse(BaseModel):
    """Response schema for conversations history."""
    
    ok: bool
    messages: Optional[List[Message]] = None
    has_more: Optional[bool] = None
    pin_count: Optional[int] = None
    response_metadata: Optional[Dict[str, Any]] = None


class ConversationsRepliesResponse(BaseModel):
    """Response schema for conversations replies."""
    
    ok: bool
    messages: Optional[List[Message]] = None
    has_more: Optional[bool] = None
    response_metadata: Optional[Dict[str, Any]] = None


class SearchMessagesResponse(BaseModel):
    """Response schema for search messages."""
    
    ok: bool
    query: Optional[str] = None
    messages: Optional[Dict[str, Any]] = None
    paging: Optional[Dict[str, Any]] = None
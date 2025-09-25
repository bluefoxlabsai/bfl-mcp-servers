"""Microsoft Teams data models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TeamsUser(BaseModel):
    """Represents a Teams user."""
    
    id: str = Field(description="User ID")
    display_name: str = Field(description="Display name")
    email: Optional[str] = Field(default=None, description="Email address")
    user_principal_name: Optional[str] = Field(default=None, description="User principal name")


class TeamsMessage(BaseModel):
    """Represents a Teams message."""
    
    id: str = Field(description="Message ID")
    content: str = Field(description="Message content")
    created_datetime: Optional[datetime] = Field(default=None, description="Creation time")
    last_modified_datetime: Optional[datetime] = Field(default=None, description="Last modified time")
    message_type: Optional[str] = Field(default=None, description="Message type")
    from_user: Optional[TeamsUser] = Field(default=None, description="Message sender")
    web_url: Optional[str] = Field(default=None, description="Web URL to message")
    importance: Optional[str] = Field(default=None, description="Message importance")
    locale: Optional[str] = Field(default=None, description="Message locale")


class TeamsChannel(BaseModel):
    """Represents a Teams channel."""
    
    id: str = Field(description="Channel ID")
    display_name: str = Field(description="Channel display name")
    description: Optional[str] = Field(default=None, description="Channel description")
    web_url: Optional[str] = Field(default=None, description="Web URL to channel")
    membership_type: Optional[str] = Field(default=None, description="Membership type")
    created_datetime: Optional[datetime] = Field(default=None, description="Creation time")
    email: Optional[str] = Field(default=None, description="Channel email")


class TeamsTeam(BaseModel):
    """Represents a Teams team."""
    
    id: str = Field(description="Team ID")
    display_name: str = Field(description="Team display name")
    description: Optional[str] = Field(default=None, description="Team description")
    web_url: Optional[str] = Field(default=None, description="Web URL to team")
    created_datetime: Optional[datetime] = Field(default=None, description="Creation time")
    visibility: Optional[str] = Field(default=None, description="Team visibility")
    specialization: Optional[str] = Field(default=None, description="Team specialization")
    is_archived: Optional[bool] = Field(default=None, description="Whether team is archived")


class TeamsChat(BaseModel):
    """Represents a Teams chat."""
    
    id: str = Field(description="Chat ID")
    topic: Optional[str] = Field(default=None, description="Chat topic")
    created_datetime: Optional[datetime] = Field(default=None, description="Creation time")
    last_updated_datetime: Optional[datetime] = Field(default=None, description="Last updated time")
    chat_type: Optional[str] = Field(default=None, description="Chat type")
    web_url: Optional[str] = Field(default=None, description="Web URL to chat")
    members: Optional[List[TeamsUser]] = Field(default=None, description="Chat members")


class TeamsMeeting(BaseModel):
    """Represents a Teams meeting."""
    
    id: str = Field(description="Meeting ID")
    subject: str = Field(description="Meeting subject")
    start_time: Optional[datetime] = Field(default=None, description="Start time")
    end_time: Optional[datetime] = Field(default=None, description="End time")
    organizer: Optional[TeamsUser] = Field(default=None, description="Meeting organizer")
    attendees: Optional[List[TeamsUser]] = Field(default=None, description="Meeting attendees")
    web_url: Optional[str] = Field(default=None, description="Web URL to meeting")
    join_url: Optional[str] = Field(default=None, description="Join URL")
    is_online_meeting: Optional[bool] = Field(default=None, description="Whether it's an online meeting")
    location: Optional[str] = Field(default=None, description="Meeting location")


class TeamsFile(BaseModel):
    """Represents a Teams file."""
    
    id: str = Field(description="File ID")
    name: str = Field(description="File name")
    size: Optional[int] = Field(default=None, description="File size in bytes")
    created_datetime: Optional[datetime] = Field(default=None, description="Creation time")
    last_modified_datetime: Optional[datetime] = Field(default=None, description="Last modified time")
    created_by: Optional[TeamsUser] = Field(default=None, description="Created by user")
    last_modified_by: Optional[TeamsUser] = Field(default=None, description="Last modified by user")
    web_url: Optional[str] = Field(default=None, description="Web URL to file")
    download_url: Optional[str] = Field(default=None, description="Download URL")
    content_type: Optional[str] = Field(default=None, description="MIME content type")


class TeamsSearchResult(BaseModel):
    """Represents a Teams search result."""
    
    id: str = Field(description="Result ID")
    title: str = Field(description="Result title")
    summary: Optional[str] = Field(default=None, description="Result summary")
    web_url: Optional[str] = Field(default=None, description="Web URL to result")
    resource_type: Optional[str] = Field(default=None, description="Resource type")
    created_datetime: Optional[datetime] = Field(default=None, description="Creation time")
    last_modified_datetime: Optional[datetime] = Field(default=None, description="Last modified time")
    created_by: Optional[TeamsUser] = Field(default=None, description="Created by user")


class TeamsActivity(BaseModel):
    """Represents a Teams activity."""
    
    id: str = Field(description="Activity ID")
    activity_type: str = Field(description="Activity type")
    created_datetime: Optional[datetime] = Field(default=None, description="Creation time")
    from_user: Optional[TeamsUser] = Field(default=None, description="Activity initiator")
    summary: Optional[str] = Field(default=None, description="Activity summary")
    web_url: Optional[str] = Field(default=None, description="Web URL to activity")


class TeamsApp(BaseModel):
    """Represents a Teams app."""
    
    id: str = Field(description="App ID")
    display_name: str = Field(description="App display name")
    description: Optional[str] = Field(default=None, description="App description")
    version: Optional[str] = Field(default=None, description="App version")
    publisher_name: Optional[str] = Field(default=None, description="Publisher name")
    app_definitions: Optional[List[Dict[str, Any]]] = Field(default=None, description="App definitions")


class TeamsTab(BaseModel):
    """Represents a Teams tab."""
    
    id: str = Field(description="Tab ID")
    display_name: str = Field(description="Tab display name")
    web_url: Optional[str] = Field(default=None, description="Web URL to tab")
    configuration: Optional[Dict[str, Any]] = Field(default=None, description="Tab configuration")
    teams_app: Optional[TeamsApp] = Field(default=None, description="Associated Teams app")
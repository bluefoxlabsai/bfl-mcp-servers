"""Microsoft Teams client implementation."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import msal
from msgraph_core import GraphRequestAdapter
from azure.identity import ClientSecretCredential
import httpx

from mcp_teams.models.teams import (
    TeamsChannel,
    TeamsChat,
    TeamsFile,
    TeamsMeeting,
    TeamsMessage,
    TeamsSearchResult,
    TeamsTeam,
    TeamsUser,
)

logger = logging.getLogger(__name__)


class TeamsClient:
    """Microsoft Teams client for interacting with Teams via Microsoft Graph API."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
    ):
        """Initialize Teams client.
        
        Args:
            client_id: Azure AD client ID
            client_secret: Azure AD client secret
            tenant_id: Azure AD tenant ID
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self._credential: Optional[ClientSecretCredential] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        
    async def _get_credential(self) -> ClientSecretCredential:
        """Get Azure credential."""
        if self._credential is None:
            self._credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        return self._credential
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get HTTP client with authentication."""
        if self._http_client is None:
            credential = await self._get_credential()
            token = await credential.get_token("https://graph.microsoft.com/.default")
            
            headers = {
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json"
            }
            
            self._http_client = httpx.AsyncClient(
                base_url="https://graph.microsoft.com/v1.0",
                headers=headers
            )
        
        return self._http_client
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Microsoft Graph API."""
        client = await self._get_http_client()
        
        response = await client.request(
            method=method,
            url=endpoint,
            json=data,
            params=params
        )
        
        response.raise_for_status()
        return response.json()
    
    async def get_my_teams(self) -> List[TeamsTeam]:
        """Get teams the current user is a member of."""
        try:
            response = await self._make_request("GET", "/me/joinedTeams")
            teams = []
            
            for team_data in response.get("value", []):
                teams.append(TeamsTeam(
                    id=team_data["id"],
                    display_name=team_data["displayName"],
                    description=team_data.get("description"),
                    web_url=team_data.get("webUrl"),
                    created_datetime=team_data.get("createdDateTime"),
                    visibility=team_data.get("visibility"),
                    specialization=team_data.get("specialization"),
                    is_archived=team_data.get("isArchived"),
                ))
            
            return teams
        except Exception as e:
            logger.error(f"Error getting teams: {e}")
            raise
    
    async def get_team_channels(self, team_id: str) -> List[TeamsChannel]:
        """Get channels in a team."""
        try:
            response = await self._make_request("GET", f"/teams/{team_id}/channels")
            channels = []
            
            for channel_data in response.get("value", []):
                channels.append(TeamsChannel(
                    id=channel_data["id"],
                    display_name=channel_data["displayName"],
                    description=channel_data.get("description"),
                    web_url=channel_data.get("webUrl"),
                    membership_type=channel_data.get("membershipType"),
                    created_datetime=channel_data.get("createdDateTime"),
                    email=channel_data.get("email"),
                ))
            
            return channels
        except Exception as e:
            logger.error(f"Error getting team channels: {e}")
            raise
    
    async def get_channel_messages(
        self, 
        team_id: str, 
        channel_id: str, 
        limit: int = 50
    ) -> List[TeamsMessage]:
        """Get messages from a channel."""
        try:
            params = {"$top": limit, "$orderby": "createdDateTime desc"}
            response = await self._make_request(
                "GET", 
                f"/teams/{team_id}/channels/{channel_id}/messages",
                params=params
            )
            
            messages = []
            for message_data in response.get("value", []):
                from_user = None
                if message_data.get("from"):
                    user_data = message_data["from"]["user"]
                    from_user = TeamsUser(
                        id=user_data["id"],
                        display_name=user_data["displayName"],
                        email=user_data.get("email"),
                        user_principal_name=user_data.get("userPrincipalName"),
                    )
                
                messages.append(TeamsMessage(
                    id=message_data["id"],
                    content=message_data.get("body", {}).get("content", ""),
                    created_datetime=message_data.get("createdDateTime"),
                    last_modified_datetime=message_data.get("lastModifiedDateTime"),
                    message_type=message_data.get("messageType"),
                    from_user=from_user,
                    web_url=message_data.get("webUrl"),
                    importance=message_data.get("importance"),
                    locale=message_data.get("locale"),
                ))
            
            return messages
        except Exception as e:
            logger.error(f"Error getting channel messages: {e}")
            raise
    
    async def send_channel_message(
        self, 
        team_id: str, 
        channel_id: str, 
        content: str,
        content_type: str = "html"
    ) -> TeamsMessage:
        """Send a message to a channel."""
        try:
            message_data = {
                "body": {
                    "contentType": content_type,
                    "content": content
                }
            }
            
            response = await self._make_request(
                "POST",
                f"/teams/{team_id}/channels/{channel_id}/messages",
                data=message_data
            )
            
            return TeamsMessage(
                id=response["id"],
                content=response.get("body", {}).get("content", ""),
                created_datetime=response.get("createdDateTime"),
                message_type=response.get("messageType"),
                web_url=response.get("webUrl"),
            )
        except Exception as e:
            logger.error(f"Error sending channel message: {e}")
            raise
    
    async def get_my_chats(self, limit: int = 50) -> List[TeamsChat]:
        """Get user's chats."""
        try:
            params = {"$top": limit, "$orderby": "lastUpdatedDateTime desc"}
            response = await self._make_request("GET", "/me/chats", params=params)
            
            chats = []
            for chat_data in response.get("value", []):
                chats.append(TeamsChat(
                    id=chat_data["id"],
                    topic=chat_data.get("topic"),
                    created_datetime=chat_data.get("createdDateTime"),
                    last_updated_datetime=chat_data.get("lastUpdatedDateTime"),
                    chat_type=chat_data.get("chatType"),
                    web_url=chat_data.get("webUrl"),
                ))
            
            return chats
        except Exception as e:
            logger.error(f"Error getting chats: {e}")
            raise
    
    async def get_chat_messages(self, chat_id: str, limit: int = 50) -> List[TeamsMessage]:
        """Get messages from a chat."""
        try:
            params = {"$top": limit, "$orderby": "createdDateTime desc"}
            response = await self._make_request(
                "GET",
                f"/me/chats/{chat_id}/messages",
                params=params
            )
            
            messages = []
            for message_data in response.get("value", []):
                from_user = None
                if message_data.get("from"):
                    user_data = message_data["from"]["user"]
                    from_user = TeamsUser(
                        id=user_data["id"],
                        display_name=user_data["displayName"],
                        email=user_data.get("email"),
                        user_principal_name=user_data.get("userPrincipalName"),
                    )
                
                messages.append(TeamsMessage(
                    id=message_data["id"],
                    content=message_data.get("body", {}).get("content", ""),
                    created_datetime=message_data.get("createdDateTime"),
                    last_modified_datetime=message_data.get("lastModifiedDateTime"),
                    message_type=message_data.get("messageType"),
                    from_user=from_user,
                    web_url=message_data.get("webUrl"),
                    importance=message_data.get("importance"),
                ))
            
            return messages
        except Exception as e:
            logger.error(f"Error getting chat messages: {e}")
            raise
    
    async def send_chat_message(
        self, 
        chat_id: str, 
        content: str,
        content_type: str = "html"
    ) -> TeamsMessage:
        """Send a message to a chat."""
        try:
            message_data = {
                "body": {
                    "contentType": content_type,
                    "content": content
                }
            }
            
            response = await self._make_request(
                "POST",
                f"/me/chats/{chat_id}/messages",
                data=message_data
            )
            
            return TeamsMessage(
                id=response["id"],
                content=response.get("body", {}).get("content", ""),
                created_datetime=response.get("createdDateTime"),
                message_type=response.get("messageType"),
                web_url=response.get("webUrl"),
            )
        except Exception as e:
            logger.error(f"Error sending chat message: {e}")
            raise
    
    async def search_messages(self, query: str, limit: int = 25) -> List[TeamsSearchResult]:
        """Search for messages across Teams."""
        try:
            search_data = {
                "requests": [
                    {
                        "entityTypes": ["chatMessage"],
                        "query": {
                            "queryString": query
                        },
                        "from": 0,
                        "size": limit
                    }
                ]
            }
            
            response = await self._make_request("POST", "/search/query", data=search_data)
            
            results = []
            for search_response in response.get("value", []):
                for hit in search_response.get("hitsContainers", []):
                    for result in hit.get("hits", []):
                        resource = result.get("resource", {})
                        results.append(TeamsSearchResult(
                            id=resource.get("id", ""),
                            title=resource.get("subject", resource.get("summary", "")),
                            summary=result.get("summary", ""),
                            web_url=resource.get("webUrl"),
                            resource_type="chatMessage",
                            created_datetime=resource.get("createdDateTime"),
                            last_modified_datetime=resource.get("lastModifiedDateTime"),
                        ))
            
            return results
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            raise
    
    async def create_meeting(
        self,
        subject: str,
        start_time: datetime,
        end_time: datetime,
        attendees: Optional[List[str]] = None
    ) -> TeamsMeeting:
        """Create a Teams meeting."""
        try:
            meeting_data = {
                "subject": subject,
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "UTC"
                },
                "isOnlineMeeting": True,
                "onlineMeetingProvider": "teamsForBusiness"
            }
            
            if attendees:
                meeting_data["attendees"] = [
                    {
                        "emailAddress": {
                            "address": email,
                            "name": email
                        },
                        "type": "required"
                    }
                    for email in attendees
                ]
            
            response = await self._make_request("POST", "/me/events", data=meeting_data)
            
            return TeamsMeeting(
                id=response["id"],
                subject=response["subject"],
                start_time=response.get("start", {}).get("dateTime"),
                end_time=response.get("end", {}).get("dateTime"),
                web_url=response.get("webUrl"),
                join_url=response.get("onlineMeeting", {}).get("joinUrl"),
                is_online_meeting=response.get("isOnlineMeeting"),
            )
        except Exception as e:
            logger.error(f"Error creating meeting: {e}")
            raise
    
    async def get_my_meetings(self, limit: int = 25) -> List[TeamsMeeting]:
        """Get user's upcoming meetings."""
        try:
            params = {
                "$top": limit,
                "$orderby": "start/dateTime",
                "$filter": f"start/dateTime ge '{datetime.utcnow().isoformat()}Z'"
            }
            
            response = await self._make_request("GET", "/me/events", params=params)
            
            meetings = []
            for meeting_data in response.get("value", []):
                meetings.append(TeamsMeeting(
                    id=meeting_data["id"],
                    subject=meeting_data["subject"],
                    start_time=meeting_data.get("start", {}).get("dateTime"),
                    end_time=meeting_data.get("end", {}).get("dateTime"),
                    web_url=meeting_data.get("webUrl"),
                    join_url=meeting_data.get("onlineMeeting", {}).get("joinUrl"),
                    is_online_meeting=meeting_data.get("isOnlineMeeting"),
                    location=meeting_data.get("location", {}).get("displayName"),
                ))
            
            return meetings
        except Exception as e:
            logger.error(f"Error getting meetings: {e}")
            raise
    
    async def create_channel(
        self, 
        team_id: str, 
        display_name: str, 
        description: Optional[str] = None
    ) -> TeamsChannel:
        """Create a new channel in a team."""
        try:
            channel_data = {
                "displayName": display_name,
                "description": description or "",
                "membershipType": "standard"
            }
            
            response = await self._make_request(
                "POST",
                f"/teams/{team_id}/channels",
                data=channel_data
            )
            
            return TeamsChannel(
                id=response["id"],
                display_name=response["displayName"],
                description=response.get("description"),
                web_url=response.get("webUrl"),
                membership_type=response.get("membershipType"),
                created_datetime=response.get("createdDateTime"),
            )
        except Exception as e:
            logger.error(f"Error creating channel: {e}")
            raise
    
    async def get_channel_files(self, team_id: str, channel_id: str) -> List[TeamsFile]:
        """Get files in a channel."""
        try:
            response = await self._make_request(
                "GET",
                f"/teams/{team_id}/channels/{channel_id}/filesFolder/children"
            )
            
            files = []
            for file_data in response.get("value", []):
                files.append(TeamsFile(
                    id=file_data["id"],
                    name=file_data["name"],
                    size=file_data.get("size"),
                    created_datetime=file_data.get("createdDateTime"),
                    last_modified_datetime=file_data.get("lastModifiedDateTime"),
                    web_url=file_data.get("webUrl"),
                    content_type=file_data.get("file", {}).get("mimeType"),
                ))
            
            return files
        except Exception as e:
            logger.error(f"Error getting channel files: {e}")
            raise
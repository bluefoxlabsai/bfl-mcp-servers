"""Tests for Microsoft Teams client."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from mcp_teams.teams.client import TeamsClient


class TestTeamsClient:
    """Test cases for TeamsClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TeamsClient(
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id"
        )
    
    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.client_id == "test-client-id"
        assert self.client.client_secret == "test-client-secret"
        assert self.client.tenant_id == "test-tenant-id"
        assert self.client._credential is None
        assert self.client._http_client is None
    
    @patch('mcp_teams.teams.client.ClientSecretCredential')
    async def test_get_credential(self, mock_credential_class):
        """Test credential creation."""
        mock_credential = Mock()
        mock_credential_class.return_value = mock_credential
        
        credential = await self.client._get_credential()
        
        assert credential == mock_credential
        mock_credential_class.assert_called_once_with(
            tenant_id="test-tenant-id",
            client_id="test-client-id",
            client_secret="test-client-secret"
        )
    
    @patch('mcp_teams.teams.client.httpx.AsyncClient')
    @patch.object(TeamsClient, '_get_credential')
    async def test_get_http_client(self, mock_get_credential, mock_http_client_class):
        """Test HTTP client creation."""
        # Mock credential and token
        mock_credential = Mock()
        mock_token = Mock()
        mock_token.token = "test-access-token"
        mock_credential.get_token = AsyncMock(return_value=mock_token)
        mock_get_credential.return_value = mock_credential
        
        # Mock HTTP client
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client
        
        # Test
        http_client = await self.client._get_http_client()
        
        # Assertions
        assert http_client == mock_http_client
        mock_credential.get_token.assert_called_once_with("https://graph.microsoft.com/.default")
        mock_http_client_class.assert_called_once()
    
    @patch.object(TeamsClient, '_make_request')
    async def test_get_my_teams(self, mock_make_request):
        """Test getting user's teams."""
        # Mock API response
        mock_response = {
            "value": [
                {
                    "id": "team-1",
                    "displayName": "Test Team 1",
                    "description": "Test team description",
                    "webUrl": "https://teams.microsoft.com/l/team/team-1",
                    "visibility": "private"
                },
                {
                    "id": "team-2",
                    "displayName": "Test Team 2",
                    "visibility": "public"
                }
            ]
        }
        mock_make_request.return_value = mock_response
        
        # Test
        teams = await self.client.get_my_teams()
        
        # Assertions
        assert len(teams) == 2
        assert teams[0].id == "team-1"
        assert teams[0].display_name == "Test Team 1"
        assert teams[0].description == "Test team description"
        assert teams[1].id == "team-2"
        assert teams[1].display_name == "Test Team 2"
        mock_make_request.assert_called_once_with("GET", "/me/joinedTeams")
    
    @patch.object(TeamsClient, '_make_request')
    async def test_send_channel_message(self, mock_make_request):
        """Test sending a message to a channel."""
        # Mock API response
        mock_response = {
            "id": "message-1",
            "body": {
                "content": "Test message content"
            },
            "createdDateTime": "2024-01-01T12:00:00Z",
            "messageType": "message",
            "webUrl": "https://teams.microsoft.com/l/message/message-1"
        }
        mock_make_request.return_value = mock_response
        
        # Test
        message = await self.client.send_channel_message(
            "team-1", 
            "channel-1", 
            "Test message content"
        )
        
        # Assertions
        assert message.id == "message-1"
        assert message.content == "Test message content"
        assert message.message_type == "message"
        
        # Verify the request was made correctly
        expected_data = {
            "body": {
                "contentType": "html",
                "content": "Test message content"
            }
        }
        mock_make_request.assert_called_once_with(
            "POST",
            "/teams/team-1/channels/channel-1/messages",
            data=expected_data
        )
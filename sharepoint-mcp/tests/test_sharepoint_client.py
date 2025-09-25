"""Tests for SharePoint client."""

import pytest
from unittest.mock import Mock, patch

from mcp_sharepoint.sharepoint.client import SharePointClient


class TestSharePointClient:
    """Test cases for SharePointClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = SharePointClient(
            site_url="https://test.sharepoint.com/sites/test",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id"
        )
    
    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.site_url == "https://test.sharepoint.com/sites/test"
        assert self.client.client_id == "test-client-id"
        assert self.client.client_secret == "test-client-secret"
        assert self.client.tenant_id == "test-tenant-id"
        assert self.client._context is None
    
    @patch('mcp_sharepoint.sharepoint.client.msal.ConfidentialClientApplication')
    @patch('mcp_sharepoint.sharepoint.client.ClientContext')
    async def test_get_context_success(self, mock_client_context, mock_msal_app):
        """Test successful context creation."""
        # Mock MSAL app
        mock_app_instance = Mock()
        mock_app_instance.acquire_token_for_client.return_value = {
            "access_token": "test-token"
        }
        mock_msal_app.return_value = mock_app_instance
        
        # Mock ClientContext
        mock_context_instance = Mock()
        mock_client_context.return_value = mock_context_instance
        
        # Test
        context = await self.client._get_context()
        
        # Assertions
        assert context == mock_context_instance
        mock_msal_app.assert_called_once()
        mock_app_instance.acquire_token_for_client.assert_called_once()
        mock_context_instance.with_access_token.assert_called_once_with("test-token")
    
    @patch('mcp_sharepoint.sharepoint.client.msal.ConfidentialClientApplication')
    async def test_get_context_auth_failure(self, mock_msal_app):
        """Test context creation with authentication failure."""
        # Mock MSAL app with auth failure
        mock_app_instance = Mock()
        mock_app_instance.acquire_token_for_client.return_value = {
            "error": "invalid_client",
            "error_description": "Invalid client credentials"
        }
        mock_msal_app.return_value = mock_app_instance
        
        # Test
        with pytest.raises(Exception) as exc_info:
            await self.client._get_context()
        
        assert "Failed to acquire token" in str(exc_info.value)
    
    @patch.object(SharePointClient, '_get_context')
    async def test_get_site_info(self, mock_get_context):
        """Test getting site information."""
        # Mock context and web
        mock_web = Mock()
        mock_web.id = "test-site-id"
        mock_web.title = "Test Site"
        mock_web.url = "https://test.sharepoint.com/sites/test"
        mock_web.description = "Test site description"
        mock_web.created = "2024-01-01T00:00:00Z"
        mock_web.last_item_modified_date = "2024-01-02T00:00:00Z"
        mock_web.web_template = "STS#3"
        
        mock_context = Mock()
        mock_context.web = mock_web
        mock_get_context.return_value = mock_context
        
        # Test
        site_info = await self.client.get_site_info()
        
        # Assertions
        assert site_info.id == "test-site-id"
        assert site_info.title == "Test Site"
        assert site_info.url == "https://test.sharepoint.com/sites/test"
        mock_context.load.assert_called_once_with(mock_web)
        mock_context.execute_query.assert_called_once()
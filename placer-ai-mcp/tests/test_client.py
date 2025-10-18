"""Unit tests for the PlacerAI API client."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from mcp_placer_ai.client import PlacerAIClient
from mcp_placer_ai.exceptions import PlacerAIAPIError, PlacerAIRateLimitError


class TestPlacerAIClient:
    """Test cases for PlacerAI API client."""

    @pytest.fixture
    def client(self, api_key, base_url):
        """Create a PlacerAI client instance."""
        return PlacerAIClient(api_key=api_key, base_url=base_url)

    @pytest.mark.asyncio
    async def test_client_initialization(self, client, api_key, base_url):
        """Test client initialization."""
        assert client.api_key == api_key
        assert client.base_url == base_url
        assert client.timeout == 30  # default

    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test client as async context manager."""
        async with client as c:
            assert c is client
            assert client._client is not None

    @pytest.mark.asyncio
    async def test_search_locations_success(
        self, client, sample_location_search_response
    ):
        """Test successful location search."""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_location_search_response
            
            result = await client.search_locations(
                query="Starbucks",
                location="San Francisco, CA",
                limit=10
            )
            
            assert result == sample_location_search_response
            mock_request.assert_called_once_with(
                "GET",
                "/locations/search",
                params={
                    "query": "Starbucks",
                    "location": "San Francisco, CA",
                    "limit": 10
                }
            )

    @pytest.mark.asyncio
    async def test_get_visits_analysis_success(
        self, client, sample_visits_analysis_response
    ):
        """Test successful visits analysis."""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_visits_analysis_response
            
            result = await client.get_visits_analysis(
                location_id="loc_12345",
                start_date="2024-01-01",
                end_date="2024-01-31"
            )
            
            assert result == sample_visits_analysis_response
            mock_request.assert_called_once_with(
                "GET",
                "/locations/loc_12345/visits",
                params={
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31"
                }
            )

    @pytest.mark.asyncio
    async def test_get_demographics_analysis_success(
        self, client, sample_demographics_response
    ):
        """Test successful demographics analysis."""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_demographics_response
            
            result = await client.get_demographics_analysis(
                location_id="loc_12345",
                start_date="2024-01-01",
                end_date="2024-01-31",
                demographic_types=["age", "income"]
            )
            
            assert result == sample_demographics_response
            mock_request.assert_called_once_with(
                "GET",
                "/locations/loc_12345/demographics",
                params={
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "demographic_types": ["age", "income"]
                }
            )

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client):
        """Test API error handling."""
        with patch.object(client, '_client') as mock_client:
            # Mock 401 Unauthorized
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "Invalid API key"}
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "401 Unauthorized", request=Mock(), response=mock_response
            )
            mock_client.get = AsyncMock(return_value=mock_response)
            
            with pytest.raises(PlacerAIAPIError) as exc_info:
                await client.search_locations("test")
            
            assert "401" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, client):
        """Test rate limit error handling."""
        with patch.object(client, '_client') as mock_client:
            # Mock 429 Rate Limited
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {"error": "Rate limit exceeded"}
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "429 Too Many Requests", request=Mock(), response=mock_response
            )
            mock_client.get = AsyncMock(return_value=mock_response)
            
            with pytest.raises(PlacerAIRateLimitError):
                await client.search_locations("test")

    @pytest.mark.asyncio
    async def test_cache_functionality(self, client):
        """Test caching functionality."""
        with patch.object(client, '_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"test": "data"}
            mock_client.get = AsyncMock(return_value=mock_response)
            
            # First call should hit the API
            result1 = await client.search_locations("test")
            assert mock_client.get.call_count == 1
            
            # Second call with same parameters should use cache
            result2 = await client.search_locations("test")
            assert mock_client.get.call_count == 1  # No additional API call
            assert result1 == result2

    @pytest.mark.asyncio
    async def test_make_request_headers(self, client):
        """Test that requests include proper headers."""
        with patch.object(client, '_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"test": "data"}
            mock_client.get = AsyncMock(return_value=mock_response)
            
            await client._make_request("GET", "/test")
            
            # Verify headers were set correctly
            call_args = mock_client.get.call_args
            headers = call_args.kwargs.get('headers', {})
            assert headers.get('Authorization') == f"Bearer {client.api_key}"
            assert headers.get('Content-Type') == 'application/json'
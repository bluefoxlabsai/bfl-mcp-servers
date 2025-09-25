"""Tests for AccuWeather MCP server."""

import pytest
from unittest.mock import Mock, patch
from mcp_accuweather.server import create_server
from mcp_accuweather.client import AccuWeatherClient
from mcp_accuweather.exceptions import AuthenticationError, LocationNotFoundError


class TestAccuWeatherServer:
    """Test cases for AccuWeather MCP server."""

    def test_create_server(self):
        """Test server creation."""
        with patch.dict('os.environ', {'ACCUWEATHER_API_KEY': 'test_key'}):
            server = create_server()
            assert server is not None
            assert hasattr(server, 'run')

    @pytest.mark.asyncio
    async def test_location_search_success(self):
        """Test successful location search."""
        with patch.dict('os.environ', {'ACCUWEATHER_API_KEY': 'test_key'}):
            client = AccuWeatherClient()
            
            # Mock the HTTP response
            mock_response = [
                {
                    "Version": 1,
                    "Key": "349727",
                    "Type": "City",
                    "Rank": 10,
                    "LocalizedName": "New York",
                    "Country": {"ID": "US", "LocalizedName": "United States"},
                    "AdministrativeArea": {"ID": "NY", "LocalizedName": "New York"}
                }
            ]
            
            with patch.object(client, '_make_request', return_value=mock_response):
                result = await client.search_locations("New York")
                assert len(result) == 1
                assert result[0]["LocalizedName"] == "New York"

    @pytest.mark.asyncio
    async def test_location_search_not_found(self):
        """Test location search with no results."""
        with patch.dict('os.environ', {'ACCUWEATHER_API_KEY': 'test_key'}):
            client = AccuWeatherClient()
            
            with patch.object(client, '_make_request', return_value=[]):
                result = await client.search_locations("NonexistentPlace")
                assert result == []  # Empty list is returned, not an exception

    @pytest.mark.asyncio
    async def test_current_conditions_success(self):
        """Test successful current conditions retrieval."""
        with patch.dict('os.environ', {'ACCUWEATHER_API_KEY': 'test_key'}):
            client = AccuWeatherClient()
            
            mock_response = [
                {
                    "LocalObservationDateTime": "2024-01-01T12:00:00-05:00",
                    "EpochTime": 1704124800,
                    "WeatherText": "Sunny",
                    "WeatherIcon": 1,
                    "HasPrecipitation": False,
                    "Temperature": {
                        "Metric": {"Value": 20.0, "Unit": "C"},
                        "Imperial": {"Value": 68.0, "Unit": "F"}
                    },
                    "Humidity": 45,
                    "Wind": {
                        "Speed": {
                            "Metric": {"Value": 10.0, "Unit": "km/h"},
                            "Imperial": {"Value": 6.2, "Unit": "mi/h"}
                        },
                        "Direction": {"Degrees": 180, "Localized": "S"}
                    }
                }
            ]
            
            with patch.object(client, '_make_request', return_value=mock_response):
                result = await client.get_current_conditions("349727")
                # Result is a list, so we need to access the first element
                assert result[0]["WeatherText"] == "Sunny"
                assert result[0]["Temperature"]["Imperial"]["Value"] == 68.0

    @pytest.mark.asyncio
    async def test_authentication_error(self):
        """Test authentication error handling."""
        with patch.dict('os.environ', {'ACCUWEATHER_API_KEY': 'invalid_key'}):
            client = AccuWeatherClient()
            
            # Mock HTTP 401 response
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"Code": "Unauthorized", "Message": "Api Authorization failed"}
            
            with patch('httpx.AsyncClient.get', return_value=mock_response):
                with pytest.raises(AuthenticationError):
                    await client.search_locations("New York")

    def test_missing_api_key(self):
        """Test behavior when API key is missing."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(AuthenticationError, match="AccuWeather API key is required"):
                AccuWeatherClient()


if __name__ == "__main__":
    pytest.main([__file__])
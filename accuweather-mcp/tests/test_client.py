"""Tests for AccuWeather API client."""

import pytest
from unittest.mock import Mock, patch
from mcp_accuweather.client import AccuWeatherClient
from mcp_accuweather.exceptions import RateLimitError, InvalidParameterError, AccuWeatherError


class TestAccuWeatherClient:
    """Test cases for AccuWeather API client."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        with patch.dict('os.environ', {'ACCUWEATHER_API_KEY': 'test_key'}):
            return AccuWeatherClient()

    @pytest.mark.asyncio
    async def test_forecast_5day_success(self, client):
        """Test successful 5-day forecast retrieval."""
        mock_response = {
            "Headline": {
                "EffectiveDate": "2024-01-01T07:00:00-05:00",
                "Text": "Pleasant this week"
            },
            "DailyForecasts": [
                {
                    "Date": "2024-01-01T07:00:00-05:00",
                    "Temperature": {
                        "Minimum": {"Value": 45, "Unit": "F"},
                        "Maximum": {"Value": 65, "Unit": "F"}
                    },
                    "Day": {"IconPhrase": "Sunny", "HasPrecipitation": False},
                    "Night": {"IconPhrase": "Clear", "HasPrecipitation": False}
                }
            ]
        }
        
        with patch.object(client, '_make_request', return_value=mock_response):
            result = await client.get_daily_forecast("349727", days=5)
            assert "Headline" in result
            assert len(result["DailyForecasts"]) == 1

    @pytest.mark.asyncio
    async def test_hourly_forecast_success(self, client):
        """Test successful hourly forecast retrieval."""
        mock_response = [
            {
                "DateTime": "2024-01-01T12:00:00-05:00",
                "EpochDateTime": 1704124800,
                "WeatherIcon": 1,
                "IconPhrase": "Sunny",
                "Temperature": {"Value": 68, "Unit": "F"},
                "Humidity": 45,
                "Wind": {
                    "Speed": {"Value": 6.2, "Unit": "mi/h"},
                    "Direction": {"Degrees": 180, "Localized": "S"}
                }
            }
        ]
        
        with patch.object(client, '_make_request', return_value=mock_response):
            result = await client.get_hourly_forecast("349727", hours=12)
            assert len(result) == 1
            assert result[0]["IconPhrase"] == "Sunny"

    @pytest.mark.asyncio
    async def test_weather_alerts_success(self, client):
        """Test successful weather alerts retrieval."""
        mock_response = [
            {
                "AlertID": 123456,
                "Description": {"Localized": "Winter Storm Warning"},
                "Category": "winter",
                "Priority": 1,
                "Class": "warning",
                "Level": "Major",
                "Source": "NWS",
                "SourceId": 1,
                "Area": [{"Name": "New York City", "Summary": "NYC Metro Area"}]
            }
        ]
        
        with patch.object(client, '_make_request', return_value=mock_response):
            result = await client.get_weather_alerts("349727")
            assert len(result) == 1
            assert result[0]["Description"]["Localized"] == "Winter Storm Warning"

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, client):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 403  # AccuWeather uses 403 for rate limits
        mock_response.json.return_value = {"Code": "RequestsExceeded", "Message": "The allowed number of requests has been exceeded"}
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            with pytest.raises(RateLimitError):
                await client.search_locations("New York")

    @pytest.mark.asyncio
    async def test_invalid_parameter_error(self, client):
        """Test invalid parameter error handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"Code": "InvalidParameter", "Message": "Invalid location key"}
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            with pytest.raises(AccuWeatherError):  # The client raises AccuWeatherError for 400 status
                await client.get_current_conditions("invalid_key")

    @pytest.mark.asyncio
    async def test_cache_functionality(self, client):
        """Test that caching works correctly."""
        mock_response = [{"Key": "349727", "LocalizedName": "New York"}]
        
        # Test caching at the HTTP level, not the method level
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response
            
            # First call should hit the API
            result1 = await client.search_locations("New York")
            assert mock_get.call_count == 1
            
            # Second call should use cache (same parameters)
            result2 = await client.search_locations("New York")
            assert mock_get.call_count == 1  # Still 1, not 2 due to caching
            
            assert result1 == result2


if __name__ == "__main__":
    pytest.main([__file__])
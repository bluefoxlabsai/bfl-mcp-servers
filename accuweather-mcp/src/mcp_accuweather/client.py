"""AccuWeather API client implementation."""

import json
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from cachetools import TTLCache

from .exceptions import AccuWeatherError, AuthenticationError, RateLimitError


class AccuWeatherClient:
    """AccuWeather API client with caching and error handling."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        cache_ttl: int = 300,  # 5 minutes
        cache_maxsize: int = 1000,
    ):
        """Initialize the AccuWeather client.
        
        Args:
            api_key: AccuWeather API key
            base_url: API base URL
            timeout: Request timeout in seconds
            cache_ttl: Cache TTL in seconds
            cache_maxsize: Maximum cache size
        """
        self.api_key = api_key or os.getenv("ACCUWEATHER_API_KEY")
        if not self.api_key:
            raise AuthenticationError("AccuWeather API key is required")
        
        self.base_url = base_url or os.getenv(
            "ACCUWEATHER_BASE_URL", 
            "http://dataservice.accuweather.com"
        )
        self.timeout = timeout
        
        # Initialize cache
        self._cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        
        # Initialize HTTP client
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "User-Agent": "MCP-AccuWeather/1.0.0",
                "Accept": "application/json",
            }
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.aclose()
    
    def _build_url(self, endpoint: str) -> str:
        """Build full API URL."""
        return urljoin(self.base_url, endpoint)
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for request."""
        # Sort params for consistent cache keys
        sorted_params = sorted(params.items())
        return f"{endpoint}:{hash(str(sorted_params))}"
    
    async def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Make HTTP request to AccuWeather API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            use_cache: Whether to use caching
            
        Returns:
            API response data
            
        Raises:
            AccuWeatherError: For API errors
            AuthenticationError: For authentication errors
            RateLimitError: For rate limit errors
        """
        if params is None:
            params = {}
        
        # Add API key to params
        params["apikey"] = self.api_key
        
        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        url = self._build_url(endpoint)
        
        try:
            response = await self._client.get(url, params=params)
            
            # Handle different HTTP status codes
            if response.status_code == 200:
                data = response.json()
                
                # Cache successful responses
                if use_cache:
                    self._cache[cache_key] = data
                
                return data
            
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            
            elif response.status_code == 403:
                raise RateLimitError("API rate limit exceeded")
            
            elif response.status_code == 404:
                raise AccuWeatherError("Resource not found")
            
            else:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        error_msg = error_data["message"]
                except Exception:
                    pass
                
                raise AccuWeatherError(error_msg)
        
        except httpx.TimeoutException:
            raise AccuWeatherError("Request timeout")
        except httpx.RequestError as e:
            raise AccuWeatherError(f"Request error: {e}")
    
    async def search_locations(
        self, 
        query: str, 
        language: str = "en-us"
    ) -> List[Dict[str, Any]]:
        """Search for locations by query.
        
        Args:
            query: Search query (city, postal code, coordinates)
            language: Language code
            
        Returns:
            List of location results
        """
        endpoint = "/locations/v1/cities/search"
        params = {
            "q": query,
            "language": language,
            "details": "true"
        }
        
        return await self._make_request(endpoint, params)
    
    async def get_current_conditions(
        self, 
        location_key: str, 
        language: str = "en-us",
        details: bool = True
    ) -> List[Dict[str, Any]]:
        """Get current weather conditions for a location.
        
        Args:
            location_key: AccuWeather location key
            language: Language code
            details: Include detailed information
            
        Returns:
            Current conditions data
        """
        endpoint = f"/currentconditions/v1/{location_key}"
        params = {
            "language": language,
            "details": str(details).lower()
        }
        
        return await self._make_request(endpoint, params)
    
    async def get_daily_forecast(
        self, 
        location_key: str, 
        days: int = 5,
        language: str = "en-us",
        metric: bool = True
    ) -> Dict[str, Any]:
        """Get daily weather forecast.
        
        Args:
            location_key: AccuWeather location key
            days: Number of forecast days (1-15)
            language: Language code
            metric: Use metric units
            
        Returns:
            Daily forecast data
        """
        endpoint = f"/forecasts/v1/daily/{days}day/{location_key}"
        params = {
            "language": language,
            "details": "true",
            "metric": str(metric).lower()
        }
        
        return await self._make_request(endpoint, params)
    
    async def get_hourly_forecast(
        self, 
        location_key: str, 
        hours: int = 12,
        language: str = "en-us",
        metric: bool = True
    ) -> List[Dict[str, Any]]:
        """Get hourly weather forecast.
        
        Args:
            location_key: AccuWeather location key
            hours: Number of forecast hours (1, 12, 24, 72, 120)
            language: Language code
            metric: Use metric units
            
        Returns:
            Hourly forecast data
        """
        # Map hours to valid AccuWeather endpoints
        if hours <= 1:
            endpoint_hours = "1hour"
        elif hours <= 12:
            endpoint_hours = "12hour"
        elif hours <= 24:
            endpoint_hours = "24hour"
        elif hours <= 72:
            endpoint_hours = "72hour"
        else:
            endpoint_hours = "120hour"
        
        endpoint = f"/forecasts/v1/hourly/{endpoint_hours}/{location_key}"
        params = {
            "language": language,
            "details": "true",
            "metric": str(metric).lower()
        }
        
        data = await self._make_request(endpoint, params)
        
        # Limit to requested number of hours
        if isinstance(data, list) and len(data) > hours:
            data = data[:hours]
        
        return data
    
    async def get_weather_alerts(
        self, 
        location_key: str, 
        language: str = "en-us"
    ) -> List[Dict[str, Any]]:
        """Get weather alerts for a location.
        
        Args:
            location_key: AccuWeather location key
            language: Language code
            
        Returns:
            Weather alerts data
        """
        endpoint = f"/alerts/v1/{location_key}"
        params = {
            "language": language,
            "details": "true"
        }
        
        return await self._make_request(endpoint, params)
    
    async def get_historical_weather(
        self, 
        location_key: str, 
        date: str,
        language: str = "en-us"
    ) -> Dict[str, Any]:
        """Get historical weather data for a specific date.
        
        Args:
            location_key: AccuWeather location key
            date: Date in YYYY-MM-DD format
            language: Language code
            
        Returns:
            Historical weather data
        """
        endpoint = f"/currentconditions/v1/{location_key}/historical"
        params = {
            "language": language,
            "details": "true",
            "date": date
        }
        
        return await self._make_request(endpoint, params)
    
    async def get_location_by_geoposition(
        self, 
        latitude: float, 
        longitude: float,
        language: str = "en-us"
    ) -> Dict[str, Any]:
        """Get location information by geographic coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            language: Language code
            
        Returns:
            Location data
        """
        endpoint = "/locations/v1/cities/geoposition/search"
        params = {
            "q": f"{latitude},{longitude}",
            "language": language,
            "details": "true"
        }
        
        return await self._make_request(endpoint, params)
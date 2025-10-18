"""Placer.ai API client implementation."""

import json
import os
from datetime import date
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from cachetools import TTLCache

from .exceptions import (
    AuthenticationError,
    NotFoundError,
    PlacerAIError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
)
from .models import (
    CompetitorAnalysisResponse,
    DemographicsResponse,
    Location,
    TradeAreaResponse,
    VisitsAnalysisResponse,
)


class PlacerAIClient:
    """Placer.ai API client with caching and error handling."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        cache_ttl: int = 300,  # 5 minutes
        cache_maxsize: int = 1000,
    ):
        """Initialize the Placer.ai client.
        
        Args:
            api_key: Placer.ai API key
            base_url: API base URL
            timeout: Request timeout in seconds
            cache_ttl: Cache TTL in seconds
            cache_maxsize: Maximum cache size
        """
        self.api_key = api_key or os.getenv("PLACER_AI_API_KEY")
        if not self.api_key:
            raise AuthenticationError("Placer.ai API key is required")

        self.base_url = base_url or os.getenv(
            "PLACER_AI_BASE_URL", "https://api.placer.ai/v1"
        )
        self.timeout = timeout

        # Initialize cache
        self._cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

        # Initialize HTTP client
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "MCP-PlacerAI/0.1.0",
            },
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    def _get_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate cache key for request."""
        key_parts = [endpoint]
        if params:
            sorted_params = sorted(params.items())
            key_parts.extend([f"{k}={v}" for k, v in sorted_params])
        return "|".join(key_parts)

    async def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Placer.ai API."""
        url = urljoin(self.base_url, endpoint)

        # Check cache for GET requests
        if method == "GET" and params:
            cache_key = self._get_cache_key(endpoint, params)
            if cache_key in self._cache:
                return self._cache[cache_key]

        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=data,
            )

            # Handle different HTTP status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 404:
                raise NotFoundError("Resource not found")
            elif response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")
            elif response.status_code == 503:
                raise ServiceUnavailableError("Placer.ai service temporarily unavailable")
            elif response.status_code >= 400:
                raise PlacerAIError(f"API request failed: {response.text}", response.status_code)

            response.raise_for_status()
            result = response.json()

            # Cache successful GET responses
            if method == "GET" and params:
                cache_key = self._get_cache_key(endpoint, params)
                self._cache[cache_key] = result

            return result

        except httpx.TimeoutException:
            raise PlacerAIError("Request timeout - Placer.ai API did not respond in time")
        except httpx.RequestError as e:
            raise PlacerAIError(f"Network error: {str(e)}")

    async def search_locations(
        self, query: str, radius_km: float = 1.0, limit: int = 10
    ) -> List[Location]:
        """Search for locations by name or coordinates."""
        params = {
            "query": query,
            "radius": radius_km * 1000,  # Convert to meters
            "limit": limit,
        }

        result = await self._make_request("GET", "/venues/search", params=params)
        
        locations = []
        for venue_data in result.get("venues", []):
            location = Location(
                venue_id=venue_data["venue_id"],
                name=venue_data["name"],
                address=venue_data.get("address", ""),
                latitude=venue_data["location"]["lat"],
                longitude=venue_data["location"]["lng"],
                category=venue_data.get("category"),
                subcategory=venue_data.get("subcategory"),
            )
            locations.append(location)

        return locations

    async def get_visits_analysis(
        self, venue_id: str, start_date: date, end_date: date, granularity: str = "daily"
    ) -> VisitsAnalysisResponse:
        """Get visits analysis for a venue."""
        params = {
            "venue_id": venue_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "granularity": granularity,
        }

        result = await self._make_request("GET", "/analytics/visits", params=params)
        
        return VisitsAnalysisResponse(**result)

    async def get_competitor_analysis(
        self, venue_id: str, competitor_ids: List[str], start_date: date, end_date: date
    ) -> CompetitorAnalysisResponse:
        """Get competitor analysis."""
        data = {
            "primary_venue": venue_id,
            "competitors": competitor_ids,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

        result = await self._make_request("POST", "/analytics/competitors", data=data)
        
        return CompetitorAnalysisResponse(**result)

    async def get_demographics(
        self, venue_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> DemographicsResponse:
        """Get demographic analysis for a venue."""
        params = {"venue_id": venue_id}
        
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        result = await self._make_request("GET", "/analytics/demographics", params=params)
        
        return DemographicsResponse(**result)

    async def get_trade_area(self, venue_id: str, percentile: int = 80) -> TradeAreaResponse:
        """Get trade area analysis for a venue."""
        params = {
            "venue_id": venue_id,
            "percentile": percentile,
        }

        result = await self._make_request("GET", "/analytics/trade-area", params=params)
        
        return TradeAreaResponse(**result)
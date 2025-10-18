"""Test configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def api_key():
    """Return a test API key."""
    return "test_api_key_12345"

@pytest.fixture
def base_url():
    """Return the test base URL."""
    return "https://api.placer.ai/v1"

@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for testing."""
    client = Mock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client

@pytest.fixture
def sample_location_search_response():
    """Sample response for location search."""
    return {
        "locations": [
            {
                "id": "loc_12345",
                "name": "Starbucks - Union Square",
                "address": "123 Main St, San Francisco, CA 94102",
                "coordinates": {
                    "latitude": 37.7879,
                    "longitude": -122.4075
                },
                "category": "Coffee Shop",
                "brand": "Starbucks"
            },
            {
                "id": "loc_67890",
                "name": "Starbucks - Financial District",
                "address": "456 Market St, San Francisco, CA 94105",
                "coordinates": {
                    "latitude": 37.7886,
                    "longitude": -122.4001
                },
                "category": "Coffee Shop",
                "brand": "Starbucks"
            }
        ],
        "total": 2,
        "page": 1,
        "per_page": 10
    }

@pytest.fixture
def sample_visits_analysis_response():
    """Sample response for visits analysis."""
    return {
        "location_id": "loc_12345",
        "period": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        },
        "metrics": {
            "total_visits": 15420,
            "average_daily_visits": 497,
            "peak_day": "2024-01-15",
            "peak_visits": 1245,
            "busiest_hour": "09:00",
            "weekly_pattern": {
                "monday": 2150,
                "tuesday": 2180,
                "wednesday": 2200,
                "thursday": 2190,
                "friday": 2340,
                "saturday": 2180,
                "sunday": 2180
            }
        }
    }

@pytest.fixture
def sample_demographics_response():
    """Sample response for demographics analysis."""
    return {
        "location_id": "loc_12345",
        "period": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        },
        "demographics": {
            "age_groups": {
                "18-24": 0.15,
                "25-34": 0.35,
                "35-44": 0.25,
                "45-54": 0.15,
                "55-64": 0.08,
                "65+": 0.02
            },
            "income_brackets": {
                "under_50k": 0.20,
                "50k_75k": 0.25,
                "75k_100k": 0.25,
                "100k_150k": 0.20,
                "over_150k": 0.10
            },
            "interests": [
                "Technology",
                "Coffee",
                "Business",
                "Fitness",
                "Travel"
            ]
        }
    }

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch, api_key, base_url):
    """Mock environment variables for testing."""
    monkeypatch.setenv("PLACER_AI_API_KEY", api_key)
    monkeypatch.setenv("PLACER_AI_BASE_URL", base_url)
    monkeypatch.setenv("PLACER_AI_TIMEOUT", "30")
    monkeypatch.setenv("PLACER_AI_CACHE_TTL", "300")
    monkeypatch.setenv("PLACER_AI_CACHE_MAX_SIZE", "1000")
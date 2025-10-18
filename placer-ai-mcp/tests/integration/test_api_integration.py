"""Integration tests for Placer.ai MCP server.

These tests require a valid API key and make real API calls.
Run with: pytest tests/integration/ -m integration
"""

import os
import pytest
from mcp_placer_ai.client import PlacerAIClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_connection():
    """Test real API connection with valid credentials."""
    api_key = os.getenv("PLACER_AI_API_KEY")
    if not api_key:
        pytest.skip("PLACER_AI_API_KEY not set - skipping integration test")
    
    async with PlacerAIClient(api_key=api_key) as client:
        # Test a simple search that should work
        result = await client.search_locations(
            query="Starbucks",
            limit=1
        )
        
        assert isinstance(result, dict)
        assert "locations" in result or "error" not in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_api_key():
    """Test behavior with invalid API key."""
    from mcp_placer_ai.exceptions import PlacerAIAPIError
    
    async with PlacerAIClient(api_key="invalid_key") as client:
        with pytest.raises(PlacerAIAPIError):
            await client.search_locations(query="test")
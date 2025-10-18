"""Unit tests for the MCP server."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastmcp import FastMCP

from mcp_placer_ai.server import app
from mcp_placer_ai.models import (
    LocationSearchRequest,
    VisitsAnalysisRequest,
    DemographicsAnalysisRequest,
    CompetitorAnalysisRequest,
    TradeAreaAnalysisRequest
)


class TestMCPServer:
    """Test cases for MCP server."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test the health endpoint."""
        # This would require more setup to test the actual FastMCP server
        # For now, we'll test that the app is properly configured
        assert isinstance(app, FastMCP)
        assert app.name == "placer-ai"

    @pytest.mark.asyncio
    async def test_search_locations_tool(self, sample_location_search_response):
        """Test the search_locations tool."""
        request = LocationSearchRequest(
            query="Starbucks",
            location="San Francisco, CA",
            limit=10
        )
        
        with patch('mcp_placer_ai.server.client') as mock_client:
            mock_client.search_locations = AsyncMock(
                return_value=sample_location_search_response
            )
            
            # Import the function after patching
            from mcp_placer_ai.server import search_locations
            
            result = await search_locations(
                query=request.query,
                location=request.location,
                limit=request.limit
            )
            
            assert result == sample_location_search_response
            mock_client.search_locations.assert_called_once_with(
                query="Starbucks",
                location="San Francisco, CA",
                limit=10
            )

    @pytest.mark.asyncio
    async def test_get_visits_analysis_tool(self, sample_visits_analysis_response):
        """Test the get_visits_analysis tool."""
        request = VisitsAnalysisRequest(
            location_id="loc_12345",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        with patch('mcp_placer_ai.server.client') as mock_client:
            mock_client.get_visits_analysis = AsyncMock(
                return_value=sample_visits_analysis_response
            )
            
            from mcp_placer_ai.server import get_visits_analysis
            
            result = await get_visits_analysis(
                location_id=request.location_id,
                start_date=request.start_date,
                end_date=request.end_date
            )
            
            assert result == sample_visits_analysis_response
            mock_client.get_visits_analysis.assert_called_once_with(
                location_id="loc_12345",
                start_date="2024-01-01",
                end_date="2024-01-31",
                metrics=None
            )

    @pytest.mark.asyncio
    async def test_get_demographics_analysis_tool(self, sample_demographics_response):
        """Test the get_demographics_analysis tool."""
        request = DemographicsAnalysisRequest(
            location_id="loc_12345",
            start_date="2024-01-01",
            end_date="2024-01-31",
            demographic_types=["age", "income"]
        )
        
        with patch('mcp_placer_ai.server.client') as mock_client:
            mock_client.get_demographics_analysis = AsyncMock(
                return_value=sample_demographics_response
            )
            
            from mcp_placer_ai.server import get_demographics_analysis
            
            result = await get_demographics_analysis(
                location_id=request.location_id,
                start_date=request.start_date,
                end_date=request.end_date,
                demographic_types=request.demographic_types
            )
            
            assert result == sample_demographics_response

    @pytest.mark.asyncio
    async def test_competitor_analysis_tool(self):
        """Test the get_competitor_analysis tool."""
        request = CompetitorAnalysisRequest(
            primary_location_id="loc_12345",
            competitor_location_ids=["loc_67890", "loc_54321"],
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        mock_response = {
            "primary_location": {"id": "loc_12345", "visits": 15420},
            "competitors": [
                {"id": "loc_67890", "visits": 12340},
                {"id": "loc_54321", "visits": 13200}
            ],
            "comparison": {
                "market_share": 0.38,
                "relative_performance": "+15%"
            }
        }
        
        with patch('mcp_placer_ai.server.client') as mock_client:
            mock_client.get_competitor_analysis = AsyncMock(
                return_value=mock_response
            )
            
            from mcp_placer_ai.server import get_competitor_analysis
            
            result = await get_competitor_analysis(
                primary_location_id=request.primary_location_id,
                competitor_location_ids=request.competitor_location_ids,
                start_date=request.start_date,
                end_date=request.end_date
            )
            
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_trade_area_analysis_tool(self):
        """Test the get_trade_area_analysis tool."""
        request = TradeAreaAnalysisRequest(
            location_id="loc_12345",
            radius_miles=5,
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        mock_response = {
            "location_id": "loc_12345",
            "trade_area": {
                "radius_miles": 5,
                "population": 125000,
                "households": 52000,
                "avg_income": 95000
            },
            "visitor_origins": {
                "within_1_mile": 0.35,
                "1_to_3_miles": 0.40,
                "3_to_5_miles": 0.20,
                "over_5_miles": 0.05
            }
        }
        
        with patch('mcp_placer_ai.server.client') as mock_client:
            mock_client.get_trade_area_analysis = AsyncMock(
                return_value=mock_response
            )
            
            from mcp_placer_ai.server import get_trade_area_analysis
            
            result = await get_trade_area_analysis(
                location_id=request.location_id,
                radius_miles=request.radius_miles,
                start_date=request.start_date,
                end_date=request.end_date
            )
            
            assert result == mock_response

    def test_model_validation(self):
        """Test Pydantic model validation."""
        # Test valid request
        request = LocationSearchRequest(
            query="Starbucks",
            location="San Francisco, CA",
            limit=10
        )
        assert request.query == "Starbucks"
        assert request.location == "San Francisco, CA"
        assert request.limit == 10
        
        # Test default values
        request_minimal = LocationSearchRequest(query="test")
        assert request_minimal.limit == 10  # default
        assert request_minimal.location is None  # optional
        
        # Test validation error
        with pytest.raises(ValueError):
            LocationSearchRequest(query="", limit=-1)  # invalid values
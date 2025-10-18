"""Placer.ai MCP Server - FastMCP implementation."""

import json
import os
import sys
from datetime import date
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .client import PlacerAIClient
from .exceptions import (
    AuthenticationError,
    NotFoundError,
    PlacerAIError,
    RateLimitError,
    ServiceUnavailableError,
)
from .models import (
    CompetitorAnalysisRequest,
    DemographicsRequest,
    LocationSearchRequest,
    TradeAreaRequest,
    VisitsAnalysisRequest,
)

# Load environment variables
load_dotenv()

# Validate required environment variables
if not os.getenv("PLACER_AI_API_KEY"):
    print("PLACER_AI_API_KEY is not set. Please set it in your environment or .env file.")
    print("You can obtain an API key from https://www.placer.ai/")
    sys.exit(1)

# Initialize FastMCP at module level
mcp = FastMCP("Placer.ai MCP Server")


async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for Kubernetes probes."""
    return JSONResponse({"status": "ok"})


@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def _health_check_route(request: Request) -> JSONResponse:
    return await health_check(request)


@mcp.tool()
async def search_locations(request: LocationSearchRequest) -> str:
    """Search for locations by name, address, or coordinates.
    
    Use this tool to find Placer.ai venue identifiers for location analytics.
    You can search by business name, address, or geographic coordinates.
    """
    try:
        async with PlacerAIClient() as client:
            locations = await client.search_locations(
                query=request.query,
                radius_km=request.radius_km,
                limit=request.limit
            )
            
            if not locations:
                return json.dumps({
                    "error": "No locations found for the given query",
                    "query": request.query
                })
            
            # Format response for better readability
            formatted_locations = []
            for location in locations:
                formatted_locations.append({
                    "venue_id": location.venue_id,
                    "name": location.name,
                    "address": location.address,
                    "coordinates": {
                        "latitude": location.latitude,
                        "longitude": location.longitude
                    },
                    "category": location.category,
                    "subcategory": location.subcategory
                })
            
            return json.dumps({
                "locations": formatted_locations,
                "total_found": len(locations)
            }, indent=2)
            
    except AuthenticationError as e:
        return json.dumps({"error": f"Authentication error: {e}"})
    except RateLimitError as e:
        return json.dumps({"error": f"Rate limit exceeded: {e}"})
    except PlacerAIError as e:
        return json.dumps({"error": f"Placer.ai API error: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


@mcp.tool()
async def get_visits_analysis(request: VisitsAnalysisRequest) -> str:
    """Get foot traffic and visits analysis for a specific venue.
    
    Requires a venue_id from the search_locations tool.
    Returns detailed visit patterns, trends, and statistics.
    """
    try:
        async with PlacerAIClient() as client:
            analysis = await client.get_visits_analysis(
                venue_id=request.venue_id,
                start_date=request.start_date,
                end_date=request.end_date,
                granularity=request.granularity
            )
            
            return json.dumps({
                "venue_id": analysis.venue_id,
                "venue_name": analysis.venue_name,
                "analysis_period": {
                    "start_date": request.start_date.isoformat(),
                    "end_date": request.end_date.isoformat(),
                    "granularity": request.granularity
                },
                "summary": {
                    "total_visits": analysis.total_visits,
                    "average_daily_visits": analysis.average_daily_visits
                },
                "daily_data": [
                    {
                        "date": visit_data.date.isoformat(),
                        "visits": visit_data.visits,
                        "unique_visitors": visit_data.unique_visitors,
                        "dwell_time_minutes": visit_data.dwell_time_minutes
                    }
                    for visit_data in analysis.data
                ]
            }, indent=2)
            
    except AuthenticationError as e:
        return json.dumps({"error": f"Authentication error: {e}"})
    except NotFoundError as e:
        return json.dumps({"error": f"Venue not found: {e}"})
    except RateLimitError as e:
        return json.dumps({"error": f"Rate limit exceeded: {e}"})
    except PlacerAIError as e:
        return json.dumps({"error": f"Placer.ai API error: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


@mcp.tool()
async def get_competitor_analysis(request: CompetitorAnalysisRequest) -> str:
    """Perform competitive analysis comparing a venue with its competitors.
    
    Requires venue IDs from the search_locations tool.
    Compares market share, visit trends, and performance metrics.
    """
    try:
        async with PlacerAIClient() as client:
            analysis = await client.get_competitor_analysis(
                venue_id=request.venue_id,
                competitor_ids=request.competitor_ids,
                start_date=request.start_date,
                end_date=request.end_date
            )
            
            return json.dumps({
                "analysis_period": {
                    "start_date": analysis.analysis_period[0].isoformat(),
                    "end_date": analysis.analysis_period[1].isoformat()
                },
                "primary_venue": {
                    "venue_id": analysis.primary_venue.venue_id,
                    "venue_name": analysis.primary_venue.venue_name,
                    "visits": analysis.primary_venue.visits,
                    "market_share": analysis.primary_venue.market_share,
                    "growth_rate": analysis.primary_venue.growth_rate
                },
                "competitors": [
                    {
                        "venue_id": comp.venue_id,
                        "venue_name": comp.venue_name,
                        "visits": comp.visits,
                        "market_share": comp.market_share,
                        "growth_rate": comp.growth_rate
                    }
                    for comp in analysis.competitors
                ]
            }, indent=2)
            
    except AuthenticationError as e:
        return json.dumps({"error": f"Authentication error: {e}"})
    except NotFoundError as e:
        return json.dumps({"error": f"Venue not found: {e}"})
    except RateLimitError as e:
        return json.dumps({"error": f"Rate limit exceeded: {e}"})
    except PlacerAIError as e:
        return json.dumps({"error": f"Placer.ai API error: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


@mcp.tool()
async def get_demographics_analysis(request: DemographicsRequest) -> str:
    """Get demographic analysis of venue visitors.
    
    Provides insights into age groups, income levels, and gender distribution
    of visitors to a specific venue.
    """
    try:
        async with PlacerAIClient() as client:
            demographics = await client.get_demographics(
                venue_id=request.venue_id,
                start_date=request.date_range[0] if request.date_range else None,
                end_date=request.date_range[1] if request.date_range else None
            )
            
            return json.dumps({
                "venue_id": demographics.venue_id,
                "venue_name": demographics.venue_name,
                "demographics": {
                    "age_groups": [
                        {
                            "segment": segment.segment,
                            "percentage": segment.percentage,
                            "visitor_count": segment.visitor_count
                        }
                        for segment in demographics.age_groups
                    ],
                    "income_levels": [
                        {
                            "segment": segment.segment,
                            "percentage": segment.percentage,
                            "visitor_count": segment.visitor_count
                        }
                        for segment in demographics.income_levels
                    ],
                    "gender_distribution": [
                        {
                            "segment": segment.segment,
                            "percentage": segment.percentage,
                            "visitor_count": segment.visitor_count
                        }
                        for segment in demographics.gender_distribution
                    ]
                }
            }, indent=2)
            
    except AuthenticationError as e:
        return json.dumps({"error": f"Authentication error: {e}"})
    except NotFoundError as e:
        return json.dumps({"error": f"Venue not found: {e}"})
    except RateLimitError as e:
        return json.dumps({"error": f"Rate limit exceeded: {e}"})
    except PlacerAIError as e:
        return json.dumps({"error": f"Placer.ai API error: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


@mcp.tool()
async def get_trade_area_analysis(request: TradeAreaRequest) -> str:
    """Get trade area analysis showing where venue visitors come from.
    
    Provides geographic analysis of visitor origins and trade area boundaries.
    """
    try:
        async with PlacerAIClient() as client:
            trade_area = await client.get_trade_area(
                venue_id=request.venue_id,
                percentile=request.percentile
            )
            
            return json.dumps({
                "venue_id": trade_area.venue_id,
                "venue_name": trade_area.venue_name,
                "trade_area": {
                    "percentile": trade_area.percentile,
                    "radius_km": trade_area.radius_km,
                    "geographic_boundaries": trade_area.geographic_coordinates,
                    "visitor_origins": trade_area.visitor_origins
                }
            }, indent=2)
            
    except AuthenticationError as e:
        return json.dumps({"error": f"Authentication error: {e}"})
    except NotFoundError as e:
        return json.dumps({"error": f"Venue not found: {e}"})
    except RateLimitError as e:
        return json.dumps({"error": f"Rate limit exceeded: {e}"})
    except PlacerAIError as e:
        return json.dumps({"error": f"Placer.ai API error: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


def create_server() -> FastMCP:
    """Create and configure the Placer.ai MCP server."""
    return mcp


# CLI entry point
def main():
    """Main entry point for the CLI."""
    import uvicorn
    import sys
    
    # Parse command line arguments
    transport = "streamable-http"
    host = "0.0.0.0"
    port = 8000
    
    # Simple argument parsing
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--transport" and i + 1 < len(args):
            transport = args[i + 1]
            i += 2
        elif args[i] == "--host" and i + 1 < len(args):
            host = args[i + 1]
            i += 2
        elif args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    print(f"Starting Placer.ai MCP Server with {transport} transport on port {port}")
    
    if transport == "streamable-http":
        print(f"Streamable HTTP endpoint available at: http://{host}:{port}/sse")
        # Use FastMCP's streamable HTTP app
        uvicorn.run(
            mcp.streamable_http_app,
            host=host,
            port=port,
            log_level="info"
        )
    elif transport == "sse":
        print(f"SSE endpoint available at: http://{host}:{port}")
        # Use FastMCP's SSE app
        uvicorn.run(
            mcp.sse_app,
            host=host,
            port=port,
            log_level="info"
        )
    elif transport == "stdio":
        print("Starting with stdio transport")
        # Use FastMCP's built-in stdio runner
        mcp.run()
    else:
        raise ValueError(f"Unsupported transport: {transport}")


if __name__ == "__main__":
    main()
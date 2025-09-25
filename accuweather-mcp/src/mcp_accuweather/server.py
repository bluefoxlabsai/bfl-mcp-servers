"""AccuWeather MCP Server - FastMCP implementation."""

import json
import os
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.routing import Route

from .client import AccuWeatherClient
from .exceptions import AccuWeatherError, AuthenticationError, RateLimitError
from .models import (
    CurrentConditionsRequest,
    ForecastRequest,
    HourlyForecastRequest,
    HistoricalWeatherRequest,
    LocationSearchRequest,
    WeatherAlertsRequest,
)

# Load environment variables
load_dotenv()

# Validate required environment variables
if not os.getenv("ACCUWEATHER_API_KEY"):
    print("ACCUWEATHER_API_KEY is not set. Please set it in your environment or .env file.")
    sys.exit(1)


def create_server() -> FastMCP:
    """Create and configure the AccuWeather MCP server."""
    
    # Initialize FastMCP
    mcp = FastMCP("AccuWeather MCP Server")
    
    # Health endpoint will be handled by the deployment infrastructure
    
    @mcp.tool()
    async def search_locations(request: LocationSearchRequest) -> str:
        """Search for locations by name, postal code, or coordinates.
        
        Use this tool to find AccuWeather location keys for weather queries.
        You can search by city name, postal code, or coordinates (lat,lon).
        """
        try:
            async with AccuWeatherClient() as client:
                locations = await client.search_locations(
                    query=request.query,
                    language=request.language
                )
                
                if not locations:
                    return json.dumps({
                        "error": "No locations found for the given query",
                        "query": request.query
                    })
                
                # Format response for better readability
                formatted_locations = []
                for loc in locations:
                    formatted_locations.append({
                        "key": loc.get("Key"),
                        "name": loc.get("LocalizedName"),
                        "country": loc.get("Country", {}).get("LocalizedName"),
                        "administrative_area": loc.get("AdministrativeArea", {}).get("LocalizedName"),
                        "type": loc.get("Type"),
                        "rank": loc.get("Rank")
                    })
                
                return json.dumps({
                    "locations": formatted_locations,
                    "total_found": len(locations)
                }, indent=2)
                
        except AuthenticationError as e:
            return json.dumps({"error": f"Authentication error: {e}"})
        except RateLimitError as e:
            return json.dumps({"error": f"Rate limit exceeded: {e}"})
        except AccuWeatherError as e:
            return json.dumps({"error": f"AccuWeather API error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})
    
    @mcp.tool()
    async def get_current_weather(request: CurrentConditionsRequest) -> str:
        """Get current weather conditions for a specific location.
        
        Requires a location key from the search_locations tool.
        Returns detailed current weather information including temperature,
        humidity, wind, precipitation, and more.
        """
        try:
            async with AccuWeatherClient() as client:
                conditions = await client.get_current_conditions(
                    location_key=request.location_key,
                    language=request.language,
                    details=request.details
                )
                
                if not conditions:
                    return json.dumps({
                        "error": "No current conditions found for location",
                        "location_key": request.location_key
                    })
                
                # Get the first (and usually only) condition
                current = conditions[0]
                
                # Format response
                formatted_weather = {
                    "location_key": request.location_key,
                    "observation_time": current.get("LocalObservationDateTime"),
                    "weather_text": current.get("WeatherText"),
                    "temperature": {
                        "value": current.get("Temperature", {}).get("Metric", {}).get("Value"),
                        "unit": current.get("Temperature", {}).get("Metric", {}).get("Unit")
                    },
                    "real_feel_temperature": {
                        "value": current.get("RealFeelTemperature", {}).get("Metric", {}).get("Value"),
                        "unit": current.get("RealFeelTemperature", {}).get("Metric", {}).get("Unit")
                    },
                    "humidity": current.get("RelativeHumidity"),
                    "wind": {
                        "direction": current.get("Wind", {}).get("Direction", {}).get("Localized"),
                        "speed": {
                            "value": current.get("Wind", {}).get("Speed", {}).get("Metric", {}).get("Value"),
                            "unit": current.get("Wind", {}).get("Speed", {}).get("Metric", {}).get("Unit")
                        }
                    },
                    "uv_index": current.get("UVIndex"),
                    "uv_index_text": current.get("UVIndexText"),
                    "visibility": {
                        "value": current.get("Visibility", {}).get("Metric", {}).get("Value"),
                        "unit": current.get("Visibility", {}).get("Metric", {}).get("Unit")
                    },
                    "pressure": {
                        "value": current.get("Pressure", {}).get("Metric", {}).get("Value"),
                        "unit": current.get("Pressure", {}).get("Metric", {}).get("Unit")
                    },
                    "has_precipitation": current.get("HasPrecipitation"),
                    "precipitation_type": current.get("PrecipitationType"),
                    "is_day_time": current.get("IsDayTime")
                }
                
                return json.dumps(formatted_weather, indent=2)
                
        except AuthenticationError as e:
            return json.dumps({"error": f"Authentication error: {e}"})
        except RateLimitError as e:
            return json.dumps({"error": f"Rate limit exceeded: {e}"})
        except AccuWeatherError as e:
            return json.dumps({"error": f"AccuWeather API error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})
    
    @mcp.tool()
    async def get_daily_forecast(request: ForecastRequest) -> str:
        """Get daily weather forecast for a specific location.
        
        Requires a location key from the search_locations tool.
        Returns multi-day forecast with daily high/low temperatures,
        weather conditions, and precipitation probability.
        """
        try:
            async with AccuWeatherClient() as client:
                forecast_data = await client.get_daily_forecast(
                    location_key=request.location_key,
                    days=request.days,
                    language=request.language,
                    metric=request.metric
                )
                
                if not forecast_data or "DailyForecasts" not in forecast_data:
                    return json.dumps({
                        "error": "No forecast data found for location",
                        "location_key": request.location_key
                    })
                
                # Format response
                forecasts = []
                for day in forecast_data["DailyForecasts"]:
                    formatted_day = {
                        "date": day.get("Date"),
                        "temperature": {
                            "minimum": {
                                "value": day.get("Temperature", {}).get("Minimum", {}).get("Value"),
                                "unit": day.get("Temperature", {}).get("Minimum", {}).get("Unit")
                            },
                            "maximum": {
                                "value": day.get("Temperature", {}).get("Maximum", {}).get("Value"),
                                "unit": day.get("Temperature", {}).get("Maximum", {}).get("Unit")
                            }
                        },
                        "day": {
                            "weather_text": day.get("Day", {}).get("IconPhrase"),
                            "has_precipitation": day.get("Day", {}).get("HasPrecipitation"),
                            "precipitation_type": day.get("Day", {}).get("PrecipitationType"),
                            "precipitation_probability": day.get("Day", {}).get("PrecipitationProbability")
                        },
                        "night": {
                            "weather_text": day.get("Night", {}).get("IconPhrase"),
                            "has_precipitation": day.get("Night", {}).get("HasPrecipitation"),
                            "precipitation_type": day.get("Night", {}).get("PrecipitationType"),
                            "precipitation_probability": day.get("Night", {}).get("PrecipitationProbability")
                        }
                    }
                    forecasts.append(formatted_day)
                
                return json.dumps({
                    "location_key": request.location_key,
                    "forecast_days": len(forecasts),
                    "daily_forecasts": forecasts
                }, indent=2)
                
        except AuthenticationError as e:
            return json.dumps({"error": f"Authentication error: {e}"})
        except RateLimitError as e:
            return json.dumps({"error": f"Rate limit exceeded: {e}"})
        except AccuWeatherError as e:
            return json.dumps({"error": f"AccuWeather API error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})
    
    @mcp.tool()
    async def get_hourly_forecast(request: HourlyForecastRequest) -> str:
        """Get hourly weather forecast for a specific location.
        
        Requires a location key from the search_locations tool.
        Returns detailed hourly forecast including temperature,
        precipitation probability, wind, and humidity.
        """
        try:
            async with AccuWeatherClient() as client:
                hourly_data = await client.get_hourly_forecast(
                    location_key=request.location_key,
                    hours=request.hours,
                    language=request.language,
                    metric=request.metric
                )
                
                if not hourly_data:
                    return json.dumps({
                        "error": "No hourly forecast data found for location",
                        "location_key": request.location_key
                    })
                
                # Format response
                forecasts = []
                for hour in hourly_data:
                    formatted_hour = {
                        "date_time": hour.get("DateTime"),
                        "weather_text": hour.get("IconPhrase"),
                        "temperature": {
                            "value": hour.get("Temperature", {}).get("Value"),
                            "unit": hour.get("Temperature", {}).get("Unit")
                        },
                        "real_feel_temperature": {
                            "value": hour.get("RealFeelTemperature", {}).get("Value"),
                            "unit": hour.get("RealFeelTemperature", {}).get("Unit")
                        },
                        "humidity": hour.get("RelativeHumidity"),
                        "wind": {
                            "speed": {
                                "value": hour.get("Wind", {}).get("Speed", {}).get("Value"),
                                "unit": hour.get("Wind", {}).get("Speed", {}).get("Unit")
                            },
                            "direction": hour.get("Wind", {}).get("Direction", {}).get("Localized")
                        },
                        "uv_index": hour.get("UVIndex"),
                        "precipitation_probability": hour.get("PrecipitationProbability"),
                        "has_precipitation": hour.get("HasPrecipitation"),
                        "is_daylight": hour.get("IsDaylight")
                    }
                    forecasts.append(formatted_hour)
                
                return json.dumps({
                    "location_key": request.location_key,
                    "forecast_hours": len(forecasts),
                    "hourly_forecasts": forecasts
                }, indent=2)
                
        except AuthenticationError as e:
            return json.dumps({"error": f"Authentication error: {e}"})
        except RateLimitError as e:
            return json.dumps({"error": f"Rate limit exceeded: {e}"})
        except AccuWeatherError as e:
            return json.dumps({"error": f"AccuWeather API error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})
    
    @mcp.tool()
    async def get_weather_alerts(request: WeatherAlertsRequest) -> str:
        """Get active weather alerts for a specific location.
        
        Requires a location key from the search_locations tool.
        Returns any active weather warnings, watches, or advisories.
        """
        try:
            async with AccuWeatherClient() as client:
                alerts = await client.get_weather_alerts(
                    location_key=request.location_key,
                    language=request.language
                )
                
                if not alerts:
                    return json.dumps({
                        "location_key": request.location_key,
                        "alerts": [],
                        "message": "No active weather alerts for this location"
                    })
                
                # Format response
                formatted_alerts = []
                for alert in alerts:
                    formatted_alert = {
                        "alert_id": alert.get("AlertID"),
                        "category": alert.get("Category"),
                        "classification": alert.get("Classification"),
                        "level": alert.get("Level"),
                        "priority": alert.get("Priority"),
                        "type": alert.get("Type"),
                        "source": alert.get("Source"),
                        "description": alert.get("Description", {}).get("Localized"),
                        "effective": alert.get("Effective"),
                        "expires": alert.get("Expires"),
                        "areas": [area.get("Name") for area in alert.get("Area", [])]
                    }
                    formatted_alerts.append(formatted_alert)
                
                return json.dumps({
                    "location_key": request.location_key,
                    "total_alerts": len(formatted_alerts),
                    "alerts": formatted_alerts
                }, indent=2)
                
        except AuthenticationError as e:
            return json.dumps({"error": f"Authentication error: {e}"})
        except RateLimitError as e:
            return json.dumps({"error": f"Rate limit exceeded: {e}"})
        except AccuWeatherError as e:
            return json.dumps({"error": f"AccuWeather API error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})
    
    @mcp.tool()
    async def get_location_by_coordinates(latitude: float, longitude: float, language: str = "en-us") -> str:
        """Get location information by geographic coordinates.
        
        Use this tool to find the AccuWeather location key for a specific
        latitude and longitude coordinate pair.
        """
        try:
            async with AccuWeatherClient() as client:
                location = await client.get_location_by_geoposition(
                    latitude=latitude,
                    longitude=longitude,
                    language=language
                )
                
                if not location:
                    return json.dumps({
                        "error": "No location found for the given coordinates",
                        "latitude": latitude,
                        "longitude": longitude
                    })
                
                # Format response
                formatted_location = {
                    "key": location.get("Key"),
                    "name": location.get("LocalizedName"),
                    "country": location.get("Country", {}).get("LocalizedName"),
                    "administrative_area": location.get("AdministrativeArea", {}).get("LocalizedName"),
                    "type": location.get("Type"),
                    "coordinates": {
                        "latitude": location.get("GeoPosition", {}).get("Latitude"),
                        "longitude": location.get("GeoPosition", {}).get("Longitude"),
                        "elevation": location.get("GeoPosition", {}).get("Elevation")
                    }
                }
                
                return json.dumps(formatted_location, indent=2)
                
        except AuthenticationError as e:
            return json.dumps({"error": f"Authentication error: {e}"})
        except RateLimitError as e:
            return json.dumps({"error": f"Rate limit exceeded: {e}"})
        except AccuWeatherError as e:
            return json.dumps({"error": f"AccuWeather API error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})
    
    @mcp.tool()
    async def get_historical_weather(request: HistoricalWeatherRequest) -> str:
        """Get historical weather data for a specific date and location.
        
        Requires a location key from the search_locations tool and a date
        in YYYY-MM-DD format. Returns weather conditions for that specific date.
        """
        try:
            async with AccuWeatherClient() as client:
                historical_data = await client.get_historical_weather(
                    location_key=request.location_key,
                    date=request.date,
                    language=request.language
                )
                
                if not historical_data:
                    return json.dumps({
                        "error": "No historical weather data found",
                        "location_key": request.location_key,
                        "date": request.date
                    })
                
                # Format response (historical data structure may vary)
                return json.dumps({
                    "location_key": request.location_key,
                    "date": request.date,
                    "historical_data": historical_data
                }, indent=2)
                
        except AuthenticationError as e:
            return json.dumps({"error": f"Authentication error: {e}"})
        except RateLimitError as e:
            return json.dumps({"error": f"Rate limit exceeded: {e}"})
        except AccuWeatherError as e:
            return json.dumps({"error": f"AccuWeather API error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})
    
    return mcp
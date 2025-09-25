#!/usr/bin/env python3
"""Test script for AccuWeather MCP server."""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_accuweather.client import AccuWeatherClient
from mcp_accuweather.exceptions import AccuWeatherError


async def test_client():
    """Test the AccuWeather client functionality."""
    
    # Check for API key
    api_key = os.getenv("ACCUWEATHER_API_KEY")
    if not api_key:
        print("❌ ACCUWEATHER_API_KEY environment variable is required")
        print("Please set your AccuWeather API key:")
        print("export ACCUWEATHER_API_KEY='your_api_key_here'")
        return False
    
    print(f"✅ Using API key: {api_key[:8]}...")
    
    try:
        client = AccuWeatherClient()
        
        # Test 1: Location search
        print("\n🔍 Testing location search...")
        locations = await client.search_locations("New York")
        if locations:
            location = locations[0]
            location_key = location["Key"]
            print(f"✅ Found location: {location['LocalizedName']}, {location['Country']['LocalizedName']}")
            print(f"   Location Key: {location_key}")
        else:
            print("❌ No locations found")
            return False
        
        # Test 2: Current conditions
        print("\n🌡️  Testing current conditions...")
        current = await client.get_current_conditions(location_key)
        print(f"✅ Current weather: {current['WeatherText']}")
        print(f"   Temperature: {current['Temperature']['Imperial']['Value']}°F")
        print(f"   Humidity: {current.get('Humidity', 'N/A')}%")
        
        # Test 3: 5-day forecast
        print("\n📅 Testing 5-day forecast...")
        forecast = await client.get_5day_forecast(location_key)
        print(f"✅ Forecast headline: {forecast['Headline']['Text']}")
        print(f"   Days available: {len(forecast['DailyForecasts'])}")
        
        # Test 4: Hourly forecast (12 hours)
        print("\n⏰ Testing hourly forecast...")
        hourly = await client.get_hourly_forecast(location_key, hours=12)
        print(f"✅ Hourly forecast: {len(hourly)} hours available")
        if hourly:
            print(f"   Next hour: {hourly[0]['IconPhrase']}, {hourly[0]['Temperature']['Value']}°F")
        
        # Test 5: Weather alerts
        print("\n⚠️  Testing weather alerts...")
        try:
            alerts = await client.get_weather_alerts(location_key)
            if alerts:
                print(f"✅ Found {len(alerts)} weather alerts")
                for alert in alerts[:2]:  # Show first 2 alerts
                    print(f"   - {alert['Description']['Localized']} ({alert['Level']})")
            else:
                print("✅ No weather alerts (good news!)")
        except AccuWeatherError as e:
            print(f"⚠️  Weather alerts test failed: {e}")
        
        # Test 6: Historical weather (if available)
        print("\n📊 Testing historical weather...")
        try:
            historical = await client.get_historical_weather(location_key, days=1)
            if historical:
                print(f"✅ Historical data: {len(historical)} days available")
            else:
                print("ℹ️  No historical data available (may require premium API)")
        except AccuWeatherError as e:
            print(f"ℹ️  Historical weather not available: {e}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except AccuWeatherError as e:
        print(f"❌ AccuWeather API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def test_server_tools():
    """Test the MCP server tools."""
    from mcp_accuweather.server import create_server
    
    print("\n🔧 Testing MCP server tools...")
    
    server = create_server()
    
    # Get available tools
    tools = server.list_tools()
    print(f"✅ Server created with {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")
    
    return True


def main():
    """Main test function."""
    print("🧪 AccuWeather MCP Server Test Suite")
    print("=" * 50)
    
    # Load environment variables from .env file if it exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        print(f"📁 Loading environment from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    async def run_tests():
        client_success = await test_client()
        server_success = await test_server_tools()
        
        print("\n" + "=" * 50)
        if client_success and server_success:
            print("🎉 All tests passed! The AccuWeather MCP server is ready to use.")
            return 0
        else:
            print("❌ Some tests failed. Please check the configuration and try again.")
            return 1
    
    return asyncio.run(run_tests())


if __name__ == "__main__":
    sys.exit(main())
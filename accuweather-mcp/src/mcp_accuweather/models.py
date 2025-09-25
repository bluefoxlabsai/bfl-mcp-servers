"""Pydantic models for AccuWeather API responses and requests."""

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class LocationSearchRequest(BaseModel):
    """Request model for location search."""
    query: str = Field(..., description="Location query (city, postal code, coordinates)")
    language: str = Field(default="en-us", description="Language code for response")


class CurrentConditionsRequest(BaseModel):
    """Request model for current weather conditions."""
    location_key: str = Field(..., description="AccuWeather location key")
    language: str = Field(default="en-us", description="Language code for response")
    details: bool = Field(default=True, description="Include detailed information")


class ForecastRequest(BaseModel):
    """Request model for weather forecast."""
    location_key: str = Field(..., description="AccuWeather location key")
    days: int = Field(default=5, ge=1, le=15, description="Number of forecast days (1-15)")
    language: str = Field(default="en-us", description="Language code for response")
    metric: bool = Field(default=True, description="Use metric units")


class HourlyForecastRequest(BaseModel):
    """Request model for hourly weather forecast."""
    location_key: str = Field(..., description="AccuWeather location key")
    hours: int = Field(default=12, ge=1, le=120, description="Number of forecast hours (1-120)")
    language: str = Field(default="en-us", description="Language code for response")
    metric: bool = Field(default=True, description="Use metric units")


class WeatherAlertsRequest(BaseModel):
    """Request model for weather alerts."""
    location_key: str = Field(..., description="AccuWeather location key")
    language: str = Field(default="en-us", description="Language code for response")


class HistoricalWeatherRequest(BaseModel):
    """Request model for historical weather data."""
    location_key: str = Field(..., description="AccuWeather location key")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    language: str = Field(default="en-us", description="Language code for response")


# Response Models
class LocationInfo(BaseModel):
    """Location information model."""
    key: str = Field(..., description="AccuWeather location key")
    localized_name: str = Field(..., description="Localized location name")
    english_name: str = Field(..., description="English location name")
    country: dict = Field(..., description="Country information")
    administrative_area: dict = Field(..., description="Administrative area (state/province)")
    type: str = Field(..., description="Location type")
    rank: Optional[int] = Field(None, description="Location rank")


class Temperature(BaseModel):
    """Temperature model."""
    value: float = Field(..., description="Temperature value")
    unit: str = Field(..., description="Temperature unit")
    unit_type: int = Field(..., description="Unit type code")


class WeatherCondition(BaseModel):
    """Weather condition model."""
    weather_text: str = Field(..., description="Weather description")
    weather_icon: int = Field(..., description="Weather icon number")
    has_precipitation: bool = Field(..., description="Whether precipitation is occurring")
    precipitation_type: Optional[str] = Field(None, description="Type of precipitation")
    is_day_time: bool = Field(..., description="Whether it's daytime")


class CurrentWeather(BaseModel):
    """Current weather conditions model."""
    local_observation_date_time: datetime = Field(..., description="Local observation time")
    epoch_time: int = Field(..., description="Epoch time")
    weather_text: str = Field(..., description="Weather description")
    weather_icon: int = Field(..., description="Weather icon number")
    has_precipitation: bool = Field(..., description="Whether precipitation is occurring")
    precipitation_type: Optional[str] = Field(None, description="Type of precipitation")
    is_day_time: bool = Field(..., description="Whether it's daytime")
    temperature: Temperature = Field(..., description="Current temperature")
    real_feel_temperature: Temperature = Field(..., description="Real feel temperature")
    relative_humidity: int = Field(..., description="Relative humidity percentage")
    wind: dict = Field(..., description="Wind information")
    uv_index: int = Field(..., description="UV index")
    uv_index_text: str = Field(..., description="UV index description")
    visibility: dict = Field(..., description="Visibility information")
    pressure: dict = Field(..., description="Atmospheric pressure")


class DailyForecast(BaseModel):
    """Daily forecast model."""
    date: datetime = Field(..., description="Forecast date")
    epoch_date: int = Field(..., description="Epoch date")
    temperature: dict = Field(..., description="Temperature range (min/max)")
    day: WeatherCondition = Field(..., description="Daytime conditions")
    night: WeatherCondition = Field(..., description="Nighttime conditions")
    sources: List[str] = Field(..., description="Data sources")
    mobile_link: str = Field(..., description="Mobile link")
    link: str = Field(..., description="Web link")


class HourlyForecast(BaseModel):
    """Hourly forecast model."""
    date_time: datetime = Field(..., description="Forecast datetime")
    epoch_date_time: int = Field(..., description="Epoch datetime")
    weather_icon: int = Field(..., description="Weather icon number")
    icon_phrase: str = Field(..., description="Weather description")
    has_precipitation: bool = Field(..., description="Whether precipitation is expected")
    is_day_light: bool = Field(..., description="Whether it's daylight")
    temperature: Temperature = Field(..., description="Temperature")
    real_feel_temperature: Temperature = Field(..., description="Real feel temperature")
    wind: dict = Field(..., description="Wind information")
    uv_index: int = Field(..., description="UV index")
    relative_humidity: int = Field(..., description="Relative humidity percentage")
    precipitation_probability: int = Field(..., description="Precipitation probability")


class WeatherAlert(BaseModel):
    """Weather alert model."""
    alert_id: int = Field(..., description="Alert ID")
    area: List[dict] = Field(..., description="Affected areas")
    category: str = Field(..., description="Alert category")
    classification: str = Field(..., description="Alert classification")
    level: str = Field(..., description="Alert level")
    priority: int = Field(..., description="Alert priority")
    type: str = Field(..., description="Alert type")
    type_id: int = Field(..., description="Alert type ID")
    source: str = Field(..., description="Alert source")
    source_id: int = Field(..., description="Source ID")
    disclaimer: str = Field(..., description="Disclaimer")
    description: dict = Field(..., description="Alert description")
    effective: datetime = Field(..., description="Effective time")
    expires: datetime = Field(..., description="Expiration time")
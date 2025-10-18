"""Pydantic models for Placer.ai API requests and responses."""

from datetime import date, datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class LocationSearchRequest(BaseModel):
    """Request for searching locations by name or coordinates."""
    
    query: str = Field(description="Location name, address, or coordinates")
    radius_km: Optional[float] = Field(default=1.0, description="Search radius in kilometers")
    limit: Optional[int] = Field(default=10, description="Maximum number of results")


class VisitsAnalysisRequest(BaseModel):
    """Request for analyzing visits to a location."""
    
    venue_id: str = Field(description="Placer.ai venue identifier")
    start_date: date = Field(description="Start date for analysis")
    end_date: date = Field(description="End date for analysis")
    granularity: Optional[str] = Field(default="daily", description="Data granularity (daily, weekly, monthly)")


class CompetitorAnalysisRequest(BaseModel):
    """Request for competitor analysis."""
    
    venue_id: str = Field(description="Primary venue identifier")
    competitor_ids: List[str] = Field(description="List of competitor venue identifiers")
    start_date: date = Field(description="Start date for analysis")
    end_date: date = Field(description="End date for analysis")


class DemographicsRequest(BaseModel):
    """Request for demographic analysis."""
    
    venue_id: str = Field(description="Venue identifier")
    date_range: Optional[tuple[date, date]] = Field(default=None, description="Date range for analysis")


class TradeAreaRequest(BaseModel):
    """Request for trade area analysis."""
    
    venue_id: str = Field(description="Venue identifier")
    percentile: Optional[int] = Field(default=80, description="Trade area percentile (e.g., 80 for 80% of visitors)")


# Response Models

class Location(BaseModel):
    """Location information."""
    
    venue_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    category: Optional[str] = None
    subcategory: Optional[str] = None


class VisitData(BaseModel):
    """Visit data for a specific time period."""
    
    date: date
    visits: int
    unique_visitors: int
    dwell_time_minutes: Optional[float] = None


class VisitsAnalysisResponse(BaseModel):
    """Response for visits analysis."""
    
    venue_id: str
    venue_name: str
    data: List[VisitData]
    total_visits: int
    average_daily_visits: float


class CompetitorData(BaseModel):
    """Competitor performance data."""
    
    venue_id: str
    venue_name: str
    visits: int
    market_share: float
    growth_rate: Optional[float] = None


class CompetitorAnalysisResponse(BaseModel):
    """Response for competitor analysis."""
    
    primary_venue: CompetitorData
    competitors: List[CompetitorData]
    analysis_period: tuple[date, date]


class DemographicSegment(BaseModel):
    """Demographic segment data."""
    
    segment: str
    percentage: float
    visitor_count: int


class DemographicsResponse(BaseModel):
    """Response for demographics analysis."""
    
    venue_id: str
    venue_name: str
    age_groups: List[DemographicSegment]
    income_levels: List[DemographicSegment]
    gender_distribution: List[DemographicSegment]


class TradeAreaResponse(BaseModel):
    """Response for trade area analysis."""
    
    venue_id: str
    venue_name: str
    percentile: int
    radius_km: float
    geographic_coordinates: List[tuple[float, float]]  # Polygon coordinates
    visitor_origins: List[dict]  # Top origin locations
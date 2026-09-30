"""
Jarvis AIOS — Itinerary Models
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from app.Travel.models.transport import TransportSegment


class ActivityItem(BaseModel):
    """Specific scheduled activity or sight within a day slot."""

    time_slot: Literal["morning", "afternoon", "evening"] = Field(..., description="Day slot")
    title: str = Field(..., description="Name of attraction or activity")
    description: str = Field(..., description="Contextual description and sightseeing highlights")
    location: str = Field(..., description="Neighborhood or specific landmark location")
    duration_mins: int = Field(default=120, ge=15, description="Recommended time to spend in minutes")
    estimated_cost: float = Field(default=0.0, ge=0, description="Admission fee or activity cost")
    booking_required: bool = Field(default=False, description="Whether advance booking or ticket reservation is required")
    opening_hours: Optional[str] = Field(default=None, description="Typical operating hours")
    verified_status: str = Field(default="Estimated", description="Source status ('Verified', 'Estimated')")
    booking_link: Optional[str] = Field(default=None, description="Official ticketing or booking URL")


class DayPlan(BaseModel):
    """Complete plan for a single day of the trip."""

    day_number: int = Field(..., ge=1, description="Day index (1-based)")
    date: Optional[str] = Field(default=None, description="Calendar date for this day (YYYY-MM-DD)")
    theme: str = Field(..., description="Day theme (e.g. 'Old Dubai & Heritage', 'Desert Safari Adventure')")
    activities: List[ActivityItem] = Field(default_factory=list, description="Morning, Afternoon, Evening activities")
    meal_suggestions: List[str] = Field(default_factory=list, description="Curated breakfast, lunch, and dinner recommendations")
    estimated_daily_spend: float = Field(default=0.0, ge=0, description="Estimated total activities and food spend for day")
    daily_transport: List[TransportSegment] = Field(default_factory=list, description="Key transit segments for this day")


class Itinerary(BaseModel):
    """Multi-day trip itinerary structure."""

    destination: str
    total_days: int = Field(..., ge=1)
    pace: Literal["relaxed", "balanced", "intense"] = Field(
        default="balanced",
        description="Overall pacing of the schedule",
    )
    days: List[DayPlan] = Field(default_factory=list, description="Ordered day plans")
    travel_tips: List[str] = Field(
        default_factory=list,
        description="Crucial cultural etiquette, weather notes, safety, and local guidance",
    )

"""
Jarvis AIOS — Complete Travel Plan & Booking Safety Models
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from app.Travel.models.trip_request import TripRequest
from app.Travel.models.flight import FlightOption
from app.Travel.models.hotel import HotelOption
from app.Travel.models.transport import RouteGuide
from app.Travel.models.itinerary import Itinerary
from app.Travel.models.budget import TripBudget


class TravelPlan(BaseModel):
    """Unified composite travel plan package."""

    trip_id: str = Field(..., description="Unique plan identifier")
    title: str = Field(..., description="Human-friendly trip title, e.g. '5-Day Dubai City & Desert Discovery'")
    summary: str = Field(..., description="Executive summary of the proposed plan")
    request: TripRequest = Field(..., description="Original structured trip parameters")
    flight_options: List[FlightOption] = Field(default_factory=list, description="Surfaced flight choices")
    selected_flight: Optional[FlightOption] = Field(default=None, description="Currently selected flight")
    hotel_options: List[HotelOption] = Field(default_factory=list, description="Surfaced hotel accommodations")
    selected_hotel: Optional[HotelOption] = Field(default=None, description="Currently selected hotel")
    route_guide: RouteGuide = Field(..., description="Local transport routes and airport transfers")
    itinerary: Itinerary = Field(..., description="Day-by-day sightseeing and activities schedule")
    budget: TripBudget = Field(..., description="Complete budget breakdown and solvency status")
    created_at: str = Field(..., description="ISO creation timestamp")


class BookingActionRequest(BaseModel):
    """Explicit user booking intent model with mandatory confirmation flag."""

    trip_id: str
    item_type: Literal["flight", "hotel", "activity", "transport"]
    item_id: str
    user_confirmed: bool = Field(
        ...,
        description="Mandatory user acknowledgment: Lisa will NEVER charge or book autonomously.",
    )


class BookingActionResponse(BaseModel):
    """Booking safety response with verified direct checkout/deep-link."""

    status: Literal["prepared", "confirmed_redirect", "rejected"]
    action_url: Optional[str] = None
    provider_name: str
    item_type: str
    message: str
    safety_notice: str = Field(
        default="Lisa AIOS never touches payment credentials or executes autonomous purchases. You are redirected to the official provider portal to review and finalize booking."
    )

"""
Jarvis AIOS — Flight Option Models
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class FlightSegment(BaseModel):
    """Individual flight leg in an itinerary."""

    flight_number: str = Field(..., description="Flight code, e.g. 'EK 565'")
    airline: str = Field(..., description="Airline brand, e.g. 'Emirates'")
    airline_code: str = Field(default="", description="IATA code, e.g. 'EK'")
    departure_airport: str = Field(..., description="Origin IATA or name, e.g. 'BLR'")
    arrival_airport: str = Field(..., description="Destination IATA or name, e.g. 'DXB'")
    departure_time: str = Field(..., description="Departure timestamp or ISO time")
    arrival_time: str = Field(..., description="Arrival timestamp or ISO time")
    duration_minutes: int = Field(..., ge=1, description="Duration of this leg in minutes")
    stops: int = Field(default=0, ge=0, description="Intermediate stops in this leg")
    baggage_info: Optional[str] = Field(default=None, description="Included cabin/check-in baggage")


class FlightOption(BaseModel):
    """Complete flight offer with classification rationale."""

    id: str = Field(..., description="Unique identifier for option")
    provider: str = Field(default="Google Flights", description="Underlying provider or search engine")
    category: Literal["cheapest", "fastest", "best_balance", "standard"] = Field(
        ...,
        description="Surfaced category tier",
    )
    rationale: str = Field(
        ...,
        description="Transparent justification, e.g. 'Lowest listed price', 'Shortest duration', 'Non-stop'",
    )
    price: float = Field(..., ge=0, description="Total price for all travellers")
    price_per_pax: Optional[float] = Field(default=None, description="Per passenger fare")
    currency: str = Field(default="INR", description="Currency code")
    duration_minutes: int = Field(..., ge=1, description="Total travel duration in minutes")
    stops: int = Field(default=0, ge=0, description="Total stops in journey")
    airline: str = Field(..., description="Primary airline name")
    outbound_segments: List[FlightSegment] = Field(default_factory=list, description="Outbound flight legs")
    return_segments: List[FlightSegment] = Field(default_factory=list, description="Inbound flight legs if roundtrip")
    deep_link: str = Field(..., description="Verified direct booking or search deep link")
    skyscanner_deep_link: Optional[str] = Field(default=None, description="Direct Skyscanner search link")
    makemytrip_deep_link: Optional[str] = Field(default=None, description="Direct MakeMyTrip search link")
    is_verified: bool = Field(
        default=False,
        description="True if fetched from live authenticated GDS/API; False if verified aggregator deep link",
    )
    cabin_class: str = Field(default="economy", description="Cabin class")


class FlightSearchResponse(BaseModel):
    """Results package for flight queries."""

    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    travellers: int
    flights: List[FlightOption] = Field(default_factory=list)
    has_live_gds: bool = Field(default=False)
    disclaimer: str = Field(
        default="Fares are real-time estimates or live aggregator deep links. Final price is confirmed on provider checkout."
    )

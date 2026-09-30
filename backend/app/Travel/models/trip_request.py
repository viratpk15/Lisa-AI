"""
Jarvis AIOS — Travel Request Models
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class TripRequest(BaseModel):
    """Structured travel requirements model."""

    origin: str = Field(..., description="Departure city or airport code (e.g. 'Bangalore', 'BLR')")
    destination: str = Field(..., description="Destination city or airport code (e.g. 'Dubai', 'DXB')")
    departure_date: str = Field(..., description="Departure date in YYYY-MM-DD format")
    return_date: Optional[str] = Field(None, description="Return date in YYYY-MM-DD format (optional for one-way)")
    travellers: int = Field(default=1, ge=1, le=50, description="Total number of travellers")
    budget: Optional[float] = Field(default=None, ge=0, description="Maximum total budget for trip")
    currency: str = Field(default="INR", description="Currency symbol/code (e.g. INR, USD, EUR, AED)")
    cabin_class: str = Field(
        default="economy",
        description="Flight cabin class: economy, premium_economy, business, first",
    )
    hotel_preference: Optional[str] = Field(
        default="3_to_4_star",
        description="Hotel tier or style: budget, 3_to_4_star, luxury, boutique, resort",
    )
    room_count: int = Field(default=1, ge=1, le=20, description="Number of hotel rooms required")
    travel_style: Optional[str] = Field(
        default="balanced",
        description="Travel style: relaxed, balanced, fast_paced, adventure, cultural, family",
    )
    activities: List[str] = Field(default_factory=list, description="Target activities or interests")
    food_preferences: List[str] = Field(default_factory=list, description="Dietary and cuisine preferences")
    transport_preferences: List[str] = Field(
        default_factory=list,
        description="Preferred local transit modes: metro, taxi, ride_hail, rental, walking",
    )
    accessibility_needs: Optional[str] = Field(default=None, description="Special physical or medical needs")
    raw_query: Optional[str] = Field(default=None, description="Original natural language query if parsed")

    @field_validator("origin", "destination")
    @classmethod
    def validate_locations(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Origin and destination must not be empty.")
        return cleaned

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, v: str) -> str:
        code = v.strip().upper()
        if code in ["₹", "RS", "RUPEES", "INR"]:
            return "INR"
        if code in ["$", "USD"]:
            return "USD"
        if code in ["€", "EUR"]:
            return "EUR"
        if code in ["£", "GBP"]:
            return "GBP"
        if code in ["AED", "DIRHAM"]:
            return "AED"
        return code or "INR"


class NaturalLanguageTripRequest(BaseModel):
    """Natural language trip prompt for interpretation."""

    query: str = Field(..., min_length=3, description="Natural language prompt describing travel desires")
    current_date: Optional[str] = Field(default=None, description="Grounding reference date (YYYY-MM-DD)")

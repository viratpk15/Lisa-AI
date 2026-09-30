"""
Jarvis AIOS — Hotel Option Models
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class HotelOption(BaseModel):
    """Hotel accommodation listing."""

    id: str = Field(..., description="Unique accommodation identifier")
    name: str = Field(..., description="Hotel / Resort name")
    location: str = Field(..., description="Neighborhood or area")
    address: Optional[str] = Field(default=None, description="Full address if known")
    star_rating: int = Field(default=3, ge=1, le=5, description="Official hotel star classification")
    user_rating: float = Field(default=4.0, ge=1.0, le=10.0, description="Aggregated user review score")
    reviews_count: Optional[int] = Field(default=None, description="Number of user reviews")
    price_per_night: float = Field(..., ge=0, description="Nightly room rate")
    total_price: float = Field(..., ge=0, description="Total stay price for requested room count")
    currency: str = Field(default="INR", description="Currency code")
    distance_to_center_km: Optional[float] = Field(default=None, description="Distance from central downtown / sights in km")
    amenities: List[str] = Field(default_factory=list, description="Verified amenities (WiFi, Pool, Breakfast, etc.)")
    cancellation_policy: str = Field(
        default="Standard Cancellation",
        description="Cancellation terms (e.g. 'Free cancellation until 48h prior', 'Non-refundable')",
    )
    image_url: Optional[str] = Field(default=None, description="Representative photo thumbnail")
    booking_url: str = Field(..., description="Verified direct booking / aggregator URL")
    is_verified: bool = Field(default=False, description="True if pulled from live hotel inventory API")
    rationale: str = Field(
        default="Recommended for location and amenities",
        description="Explanation of why this accommodation is surfaced",
    )


class HotelSearchResponse(BaseModel):
    """Results package for hotel search."""

    destination: str
    check_in: str
    check_out: str
    total_nights: int
    guests: int
    rooms: int
    hotels: List[HotelOption] = Field(default_factory=list)
    has_live_inventory: bool = Field(default=False)
    disclaimer: str = Field(
        default="Rates and availability are live estimates. Final booking must be executed via the provider's verified portal."
    )

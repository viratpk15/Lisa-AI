"""
Jarvis AIOS — Local Transport & Route Models
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class TransportSegment(BaseModel):
    """Local transport connection between two travel milestones."""

    segment_id: str = Field(..., description="Unique leg identifier, e.g. 'seg_airport_to_hotel'")
    from_name: str = Field(..., description="Origin location (e.g. 'Dubai International Airport DXB')")
    to_name: str = Field(..., description="Destination location (e.g. 'Downtown Hotel')")
    mode: Literal["metro", "taxi", "ride_hail", "bus", "walking", "ferry", "train"] = Field(
        ...,
        description="Suggested mode of transit",
    )
    estimated_duration_mins: int = Field(..., ge=1, description="Estimated transit duration in minutes")
    estimated_cost: float = Field(default=0.0, ge=0, description="Estimated one-way cost for travellers")
    currency: str = Field(default="INR", description="Currency code")
    is_verified: bool = Field(default=False, description="True if real-time ride pricing API was consulted")
    deep_link: Optional[str] = Field(default=None, description="App or web deep-link to order ride (Uber/Careem/Transit)")
    provider_name: Optional[str] = Field(default=None, description="Service provider (e.g. 'Dubai Metro', 'Careem', 'Uber')")
    notes: Optional[str] = Field(default=None, description="Travel tips (e.g. 'Buy Nol Silver card at Terminal 3')")


class RouteGuide(BaseModel):
    """Aggregate route guide covering transit segments and preparation items."""

    segments: List[TransportSegment] = Field(default_factory=list, description="All trip transit segments")
    total_estimated_cost: float = Field(default=0.0, ge=0, description="Sum of estimated transit costs")
    currency: str = Field(default="INR", description="Currency code")
    preparation_items: List[str] = Field(
        default_factory=list,
        description="Essential pre-departure items (visas, transit cards, currency exchange, mobile eSIM)",
    )

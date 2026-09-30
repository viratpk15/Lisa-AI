"""
Jarvis AIOS — Travel Planner Domain Models
"""

from app.Travel.models.trip_request import TripRequest, NaturalLanguageTripRequest
from app.Travel.models.flight import FlightOption, FlightSegment, FlightSearchResponse
from app.Travel.models.hotel import HotelOption, HotelSearchResponse
from app.Travel.models.transport import TransportSegment, RouteGuide
from app.Travel.models.itinerary import ActivityItem, DayPlan, Itinerary
from app.Travel.models.budget import BudgetCategory, TripBudget
from app.Travel.models.travel_plan import TravelPlan, BookingActionRequest, BookingActionResponse

__all__ = [
    "TripRequest",
    "NaturalLanguageTripRequest",
    "FlightOption",
    "FlightSegment",
    "FlightSearchResponse",
    "HotelOption",
    "HotelSearchResponse",
    "TransportSegment",
    "RouteGuide",
    "ActivityItem",
    "DayPlan",
    "Itinerary",
    "BudgetCategory",
    "TripBudget",
    "TravelPlan",
    "BookingActionRequest",
    "BookingActionResponse",
]

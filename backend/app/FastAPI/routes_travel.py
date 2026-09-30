"""
Jarvis AIOS — FastAPI Travel Planner Routes
--------------------------------------------
Endpoints for parsing natural language trip requirements, generating comprehensive
travel itineraries, querying flights/hotels, and managing booking actions with safety gates.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.Auth.dependencies import get_current_user
from app.Auth.models import User
from app.Travel.models.trip_request import TripRequest, NaturalLanguageTripRequest
from app.Travel.models.flight import FlightSearchResponse
from app.Travel.models.hotel import HotelSearchResponse
from app.Travel.models.itinerary import Itinerary
from app.Travel.models.travel_plan import TravelPlan, BookingActionRequest, BookingActionResponse
from app.Travel.services.nlp_parser import nlp_parser
from app.Travel.services.planner_service import planner_service
from app.Travel.providers.flight_provider import flight_provider
from app.Travel.providers.hotel_provider import hotel_provider, calculate_nights
from app.Travel.services.itinerary_service import itinerary_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/travel", tags=["travel"])


class SelectFlightRequest(BaseModel):
    flight_id: str


class SelectHotelRequest(BaseModel):
    hotel_id: str


@router.post(
    "/parse-prompt",
    response_model=TripRequest,
    summary="Parse Natural Language Travel Prompt",
    description="Extract structured TripRequest from a natural language travel desire prompt.",
)
def parse_travel_prompt(
    req: NaturalLanguageTripRequest,
    current_user: User = Depends(get_current_user),
) -> TripRequest:
    try:
        return nlp_parser.parse_request(req)
    except Exception as exc:
        logger.error("[TRAVEL-ROUTE] Failed to parse travel prompt: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "travel_nlp_error", "message": str(exc)}},
        )


@router.post(
    "/plan",
    response_model=TravelPlan,
    summary="Generate Complete Travel Plan",
    description="Generate flights, hotels, transport segments, multi-day itinerary, and itemized budget.",
)
def create_travel_plan(
    req: TripRequest,
    current_user: User = Depends(get_current_user),
) -> TravelPlan:
    try:
        return planner_service.create_travel_plan(req)
    except Exception as exc:
        logger.error("[TRAVEL-ROUTE] Failed to create travel plan: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "travel_plan_error", "message": str(exc)}},
        )


@router.get(
    "/plan/{trip_id}",
    response_model=TravelPlan,
    summary="Get Travel Plan by ID",
)
def get_travel_plan(
    trip_id: str,
    current_user: User = Depends(get_current_user),
) -> TravelPlan:
    plan = planner_service.get_travel_plan(trip_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "plan_not_found", "message": f"Travel plan '{trip_id}' not found."}},
        )
    return plan


@router.post(
    "/flights/search",
    response_model=FlightSearchResponse,
    summary="Search Flight Options",
)
def search_flights(
    req: TripRequest,
    current_user: User = Depends(get_current_user),
) -> FlightSearchResponse:
    flights = flight_provider.search_flights(req)
    return FlightSearchResponse(
        origin=req.origin,
        destination=req.destination,
        departure_date=req.departure_date,
        return_date=req.return_date,
        travellers=req.travellers,
        flights=flights,
        has_live_gds=False,
    )


@router.post(
    "/hotels/search",
    response_model=HotelSearchResponse,
    summary="Search Hotel Options",
)
def search_hotels(
    req: TripRequest,
    current_user: User = Depends(get_current_user),
) -> HotelSearchResponse:
    hotels = hotel_provider.search_hotels(req)
    nights = calculate_nights(req.departure_date, req.return_date)
    return HotelSearchResponse(
        destination=req.destination,
        check_in=req.departure_date,
        check_out=req.return_date or req.departure_date,
        total_nights=nights,
        guests=req.travellers,
        rooms=req.room_count,
        hotels=hotels,
        has_live_inventory=False,
    )


@router.post(
    "/itinerary/generate",
    response_model=Itinerary,
    summary="Generate Itinerary",
)
def generate_itinerary(
    req: TripRequest,
    current_user: User = Depends(get_current_user),
) -> Itinerary:
    return itinerary_service.generate_itinerary(req)


@router.post(
    "/plan/{trip_id}/select-flight",
    response_model=TravelPlan,
    summary="Select Flight and Recalculate Budget",
)
def select_flight(
    trip_id: str,
    body: SelectFlightRequest,
    current_user: User = Depends(get_current_user),
) -> TravelPlan:
    plan = planner_service.select_flight(trip_id, body.flight_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "selection_failed", "message": "Failed to update selected flight."}},
        )
    return plan


@router.post(
    "/plan/{trip_id}/select-hotel",
    response_model=TravelPlan,
    summary="Select Hotel and Recalculate Budget",
)
def select_hotel(
    trip_id: str,
    body: SelectHotelRequest,
    current_user: User = Depends(get_current_user),
) -> TravelPlan:
    plan = planner_service.select_hotel(trip_id, body.hotel_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "selection_failed", "message": "Failed to update selected hotel."}},
        )
    return plan


@router.post(
    "/booking/prepare",
    response_model=BookingActionResponse,
    summary="Prepare Booking Portal Action",
    description="Safety Gate: Validates explicit confirmation before generating verified provider booking deep-link.",
)
def prepare_booking(
    req: BookingActionRequest,
    current_user: User = Depends(get_current_user),
) -> BookingActionResponse:
    return planner_service.prepare_booking_action(req)

"""
Jarvis AIOS — Unified Travel Planner Service & Safety Coordinator
-----------------------------------------------------------------
Coordinates all Travel subsystems (Flights, Hotels, Transport, Itinerary, Budget).
Enforces zero autonomous spending and strict booking safety policies.
"""

import uuid
from datetime import datetime
from typing import Dict, Optional

from app.Travel.models.trip_request import TripRequest
from app.Travel.models.travel_plan import TravelPlan, BookingActionRequest, BookingActionResponse
from app.Travel.providers.flight_provider import flight_provider
from app.Travel.providers.hotel_provider import hotel_provider
from app.Travel.providers.transport_provider import transport_provider
from app.Travel.services.itinerary_service import itinerary_service
from app.Travel.services.budget_service import budget_service


class TravelPlannerService:
    """Core domain service orchestrating comprehensive travel planning."""

    def __init__(self) -> None:
        self._plans_cache: Dict[str, TravelPlan] = {}

    def create_travel_plan(self, request: TripRequest) -> TravelPlan:
        """Construct an end-to-end travel plan for the given request."""
        trip_id = f"trip_{uuid.uuid4().hex[:10]}"

        # 1. Search flights
        flight_options = flight_provider.search_flights(request)
        # Select best balance by default, or cheapest if explicitly tight budget
        selected_flight = flight_options[2] if len(flight_options) >= 3 else (flight_options[0] if flight_options else None)
        if request.budget and flight_options:
            cheapest = flight_options[0]
            # If best balance exceeds 50% of total budget, pick cheapest
            if selected_flight and selected_flight.price > (request.budget * 0.45):
                selected_flight = cheapest

        # 2. Search hotels
        hotel_options = hotel_provider.search_hotels(request)
        selected_hotel = hotel_options[0] if hotel_options else None

        # 3. Generate multi-day itinerary
        itinerary = itinerary_service.generate_itinerary(request)

        # 4. Extract highlights for transport mapping
        attractions = []
        for day in itinerary.days:
            for act in day.activities:
                if act.title not in attractions:
                    attractions.append(act.title)

        # 5. Build route guide and transit segments
        hotel_name = selected_hotel.name if selected_hotel else f"Hotel in {request.destination.title()}"
        route_guide = transport_provider.generate_route_guide(
            origin_city=request.origin,
            destination_city=request.destination,
            hotel_name=hotel_name,
            attractions=attractions[:4],
            currency=request.currency,
        )

        # 6. Calculate comprehensive budget
        budget = budget_service.calculate_budget(
            user_budget=request.budget,
            currency=request.currency,
            flight=selected_flight,
            hotel=selected_hotel,
            route_guide=route_guide,
            itinerary=itinerary,
            travellers=request.travellers,
        )

        title = f"{itinerary.total_days}-Day {request.destination.title()} Trip from {request.origin.title()}"
        summary = (
            f"Curated {itinerary.total_days}-day {request.travel_style} travel plan for {request.travellers} "
            f"traveller{'s' if request.travellers > 1 else ''}. Features {len(flight_options)} comparative flight options, "
            f"{len(hotel_options)} accommodations, {len(route_guide.segments)} route segments, and a {budget.status.replace('_', ' ')} budget."
        )

        plan = TravelPlan(
            trip_id=trip_id,
            title=title,
            summary=summary,
            request=request,
            flight_options=flight_options,
            selected_flight=selected_flight,
            hotel_options=hotel_options,
            selected_hotel=selected_hotel,
            route_guide=route_guide,
            itinerary=itinerary,
            budget=budget,
            created_at=datetime.now().isoformat(),
        )

        self._plans_cache[trip_id] = plan
        return plan

    def get_travel_plan(self, trip_id: str) -> Optional[TravelPlan]:
        """Retrieve existing plan from cache."""
        return self._plans_cache.get(trip_id)

    def select_flight(self, trip_id: str, flight_id: str) -> Optional[TravelPlan]:
        """Update selected flight in plan and recalculate budget."""
        plan = self._plans_cache.get(trip_id)
        if not plan:
            return None

        matching_flight = next((f for f in plan.flight_options if f.id == flight_id), None)
        if not matching_flight:
            return None

        plan.selected_flight = matching_flight
        plan.budget = budget_service.calculate_budget(
            user_budget=plan.request.budget,
            currency=plan.request.currency,
            flight=matching_flight,
            hotel=plan.selected_hotel,
            route_guide=plan.route_guide,
            itinerary=plan.itinerary,
            travellers=plan.request.travellers,
        )
        return plan

    def select_hotel(self, trip_id: str, hotel_id: str) -> Optional[TravelPlan]:
        """Update selected hotel in plan and recalculate budget."""
        plan = self._plans_cache.get(trip_id)
        if not plan:
            return None

        matching_hotel = next((h for h in plan.hotel_options if h.id == hotel_id), None)
        if not matching_hotel:
            return None

        plan.selected_hotel = matching_hotel
        plan.budget = budget_service.calculate_budget(
            user_budget=plan.request.budget,
            currency=plan.request.currency,
            flight=plan.selected_flight,
            hotel=matching_hotel,
            route_guide=plan.route_guide,
            itinerary=plan.itinerary,
            travellers=plan.request.travellers,
        )
        return plan

    def prepare_booking_action(self, req: BookingActionRequest) -> BookingActionResponse:
        """
        Enforces booking safety:
        - NEVER charges card or books autonomously.
        - Requires explicit user confirmation.
        - Returns official verified provider checkout URL.
        """
        if not req.user_confirmed:
            return BookingActionResponse(
                status="rejected",
                provider_name="Unknown",
                item_type=req.item_type,
                message="Booking action cancelled: Explicit user confirmation is required before redirecting to provider.",
            )

        plan = self._plans_cache.get(req.trip_id)
        action_url = None
        provider_name = "Official Provider"

        if req.item_type == "flight":
            flight = plan.selected_flight if plan else None
            if plan and req.item_id:
                flight = next((f for f in plan.flight_options if f.id == req.item_id), flight)
            action_url = flight.deep_link if flight else "https://www.google.com/travel/flights"
            provider_name = flight.provider if flight else "Google Flights"
        elif req.item_type == "hotel":
            hotel = plan.selected_hotel if plan else None
            if plan and req.item_id:
                hotel = next((h for h in plan.hotel_options if h.id == req.item_id), hotel)
            action_url = hotel.booking_url if hotel else "https://www.booking.com"
            provider_name = "Booking.com / Official Portal"
        elif req.item_type == "transport":
            action_url = "https://m.uber.com/ul/?action=setPickup"
            provider_name = "Uber / Local Transit"
        else:
            action_url = f"https://www.google.com/search?q={req.item_id}+tickets"
            provider_name = "Official Attraction Box Office"

        return BookingActionResponse(
            status="confirmed_redirect",
            action_url=action_url,
            provider_name=provider_name,
            item_type=req.item_type,
            message=f"Prepared booking portal for {req.item_type}. You are being redirected to {provider_name} to review fare rules and finalize your booking.",
        )


planner_service = TravelPlannerService()

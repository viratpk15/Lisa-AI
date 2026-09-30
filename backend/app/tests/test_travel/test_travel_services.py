"""
Tests for Travel Domain Services and Booking Safety
"""

from app.Travel.models.trip_request import TripRequest, NaturalLanguageTripRequest
from app.Travel.models.travel_plan import BookingActionRequest
from app.Travel.services.nlp_parser import nlp_parser
from app.Travel.providers.flight_provider import flight_provider
from app.Travel.providers.hotel_provider import hotel_provider
from app.Travel.providers.transport_provider import transport_provider
from app.Travel.services.itinerary_service import itinerary_service
from app.Travel.services.planner_service import planner_service


def test_natural_language_prompt_parser():
    nl_req = NaturalLanguageTripRequest(query="Plan a 5-day trip from Bangalore to Dubai under ₹80,000 for 2 people")
    trip_req = nlp_parser.parse_request(nl_req)

    assert "bangalore" in trip_req.origin.lower() or "blr" in trip_req.origin.lower()
    assert "dubai" in trip_req.destination.lower() or "dxb" in trip_req.destination.lower()
    assert trip_req.travellers == 2
    assert trip_req.budget == 80000.0
    assert trip_req.currency == "INR"
    assert trip_req.departure_date is not None
    assert trip_req.return_date is not None


def test_flight_search_categorization_and_rationales():
    req = TripRequest(
        origin="Bangalore",
        destination="Dubai",
        departure_date="2026-10-15",
        return_date="2026-10-20",
        travellers=1,
        budget=80000.0,
    )
    flights = flight_provider.search_flights(req)
    assert len(flights) == 3

    categories = [f.category for f in flights]
    assert "cheapest" in categories
    assert "fastest" in categories
    assert "best_balance" in categories

    cheapest = next(f for f in flights if f.category == "cheapest")
    fastest = next(f for f in flights if f.category == "fastest")
    assert cheapest.price <= fastest.price
    assert "Lowest" in cheapest.rationale or "Shortest" in fastest.rationale
    assert cheapest.deep_link.startswith("https://www.google.com/travel/flights")


def test_hotel_search_and_nights_calculation():
    req = TripRequest(
        origin="Bangalore",
        destination="Dubai",
        departure_date="2026-10-15",
        return_date="2026-10-20",
        travellers=2,
        room_count=1,
    )
    hotels = hotel_provider.search_hotels(req)
    assert len(hotels) >= 2
    for h in hotels:
        assert h.price_per_night > 0
        assert h.total_price >= h.price_per_night
        assert h.booking_url.startswith("https://www.booking.com")
        assert h.is_verified is False


def test_transport_segments_generation():
    segments = transport_provider.get_transport_segments(
        origin_city="Bangalore",
        destination_city="Dubai",
        hotel_name="Rove Downtown",
        attractions=["Burj Khalifa", "Dubai Mall"],
        currency="INR",
    )
    assert len(segments) >= 2
    modes = [s.mode for s in segments]
    assert any(m in ["metro", "taxi", "ride_hail"] for m in modes)
    for s in segments:
        assert s.estimated_duration_mins > 0
        assert s.is_verified is False


def test_itinerary_generation_and_pacing():
    req = TripRequest(
        origin="Bangalore",
        destination="Dubai",
        departure_date="2026-10-15",
        return_date="2026-10-19",
        travel_style="balanced",
    )
    itinerary = itinerary_service.generate_itinerary(req)
    assert itinerary.destination == "Dubai"
    assert len(itinerary.days) >= 4
    for day in itinerary.days:
        assert len(day.activities) >= 2
        assert len(day.meal_suggestions) >= 2
        slots = [a.time_slot for a in day.activities]
        assert "morning" in slots
        assert "afternoon" in slots


def test_budget_calculation_isolation():
    req = TripRequest(
        origin="Bangalore",
        destination="Dubai",
        departure_date="2026-10-15",
        return_date="2026-10-20",
        budget=80000.0,
        currency="INR",
        travellers=1,
    )
    plan = planner_service.create_travel_plan(req)
    budget = plan.budget

    assert budget.user_budget == 80000.0
    assert budget.total_projected > 0
    assert len(budget.categories) == 6
    # Verified amount must be 0 if using aggregator unverified deep links
    assert budget.total_verified == 0.0
    assert budget.total_estimated == budget.total_projected
    assert budget.status in ["within_budget", "exceeded"]


def test_booking_safety_explicit_confirmation_required():
    req = TripRequest(
        origin="Bangalore",
        destination="Dubai",
        departure_date="2026-10-15",
        return_date="2026-10-20",
    )
    plan = planner_service.create_travel_plan(req)

    # 1. Attempt booking action WITHOUT confirmation -> MUST REJECT
    unconfirmed_req = BookingActionRequest(
        trip_id=plan.trip_id,
        item_type="flight",
        item_id=plan.flight_options[0].id,
        user_confirmed=False,
    )
    resp = planner_service.prepare_booking_action(unconfirmed_req)
    assert resp.status == "rejected"
    assert "Explicit user confirmation is required" in resp.message
    assert resp.action_url is None

    # 2. Attempt booking action WITH confirmation -> MUST PREPARE REDIRECT (never autonomous charge)
    confirmed_req = BookingActionRequest(
        trip_id=plan.trip_id,
        item_type="flight",
        item_id=plan.flight_options[0].id,
        user_confirmed=True,
    )
    resp_confirmed = planner_service.prepare_booking_action(confirmed_req)
    assert resp_confirmed.status == "confirmed_redirect"
    assert resp_confirmed.action_url is not None
    assert "never touches payment credentials" in resp_confirmed.safety_notice

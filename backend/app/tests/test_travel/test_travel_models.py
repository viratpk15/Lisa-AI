"""
Tests for Travel Domain Models
"""

import pytest
from pydantic import ValidationError
from app.Travel.models.trip_request import TripRequest
from app.Travel.models.flight import FlightOption
from app.Travel.models.hotel import HotelOption
from app.Travel.models.transport import TransportSegment, RouteGuide
from app.Travel.models.budget import BudgetCategory, TripBudget


def test_trip_request_validation():
    req = TripRequest(
        origin="Bangalore",
        destination="Dubai",
        departure_date="2026-10-15",
        return_date="2026-10-20",
        travellers=2,
        budget=80000.0,
        currency="INR",
    )
    assert req.origin == "Bangalore"
    assert req.destination == "Dubai"
    assert req.travellers == 2
    assert req.currency == "INR"
    assert req.cabin_class == "economy"


def test_trip_request_currency_normalization():
    req1 = TripRequest(
        origin="Delhi",
        destination="London",
        departure_date="2026-11-01",
        currency="₹",
    )
    assert req1.currency == "INR"

    req2 = TripRequest(
        origin="New York",
        destination="Paris",
        departure_date="2026-11-01",
        currency="$",
    )
    assert req2.currency == "USD"


def test_trip_request_empty_location_raises():
    with pytest.raises(ValidationError):
        TripRequest(
            origin="  ",
            destination="Dubai",
            departure_date="2026-10-15",
        )


def test_flight_option_categories_and_rationale():
    flight = FlightOption(
        id="fl_test_1",
        provider="Google Flights",
        category="cheapest",
        rationale="Lowest listed price with one connection",
        price=18500.0,
        currency="INR",
        duration_minutes=360,
        stops=1,
        airline="IndiGo",
        deep_link="https://www.google.com/travel/flights",
        is_verified=False,
    )
    assert flight.category == "cheapest"
    assert "Lowest listed price" in flight.rationale
    assert flight.stops == 1
    assert flight.is_verified is False


def test_hotel_option_structure():
    hotel = HotelOption(
        id="htl_test_1",
        name="Rove Downtown",
        location="Downtown Dubai",
        star_rating=3,
        user_rating=9.1,
        price_per_night=7200.0,
        total_price=28800.0,
        currency="INR",
        booking_url="https://www.booking.com",
        is_verified=False,
        rationale="Top-rated value in Downtown",
    )
    assert hotel.name == "Rove Downtown"
    assert hotel.total_price == 28800.0
    assert hotel.star_rating == 3
    assert hotel.is_verified is False


def test_transport_segment_and_route_guide():
    seg = TransportSegment(
        segment_id="seg_1",
        from_name="DXB Airport",
        to_name="Downtown Hotel",
        mode="metro",
        estimated_duration_mins=25,
        estimated_cost=120.0,
        currency="INR",
    )
    guide = RouteGuide(
        segments=[seg],
        total_estimated_cost=120.0,
        currency="INR",
        preparation_items=["Check passport validity."],
    )
    assert len(guide.segments) == 1
    assert guide.total_estimated_cost == 120.0
    assert len(guide.preparation_items) == 1


def test_budget_breakdown_solvency():
    cats = [
        BudgetCategory(category="Flights", verified_amount=20000.0, estimated_amount=0.0, is_verified=True),
        BudgetCategory(category="Hotel", verified_amount=0.0, estimated_amount=25000.0, is_verified=False),
        BudgetCategory(category="Local transport", verified_amount=0.0, estimated_amount=3000.0),
        BudgetCategory(category="Food", verified_amount=0.0, estimated_amount=10000.0),
        BudgetCategory(category="Activities", verified_amount=0.0, estimated_amount=8000.0),
        BudgetCategory(category="Other", verified_amount=0.0, estimated_amount=4000.0),
    ]
    budget = TripBudget(
        user_budget=80000.0,
        currency="INR",
        categories=cats,
        total_verified=20000.0,
        total_estimated=50000.0,
        total_projected=70000.0,
        remaining_balance=10000.0,
        status="within_budget",
    )
    assert budget.total_verified == 20000.0
    assert budget.total_estimated == 50000.0
    assert budget.total_projected == 70000.0
    assert budget.remaining_balance == 10000.0
    assert budget.status == "within_budget"

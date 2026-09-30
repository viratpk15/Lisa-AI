"""
Tests for Travel Planner FastAPI Endpoints
"""

from fastapi.testclient import TestClient
from app.main import app
from app.Auth.security import create_access_token

client = TestClient(app)
token = create_access_token(user_id=1, email="test@example.com")
headers = {"Authorization": f"Bearer {token}"}


def test_parse_prompt_endpoint():
    resp = client.post(
        "/travel/parse-prompt",
        headers=headers,
        json={"query": "Plan a 5-day trip from Bangalore to Dubai under 80000 INR"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "bangalore" in data["origin"].lower() or "blr" in data["origin"].lower()
    assert "dubai" in data["destination"].lower() or "dxb" in data["destination"].lower()
    assert data["currency"] == "INR"


def test_create_travel_plan_endpoint():
    req_payload = {
        "origin": "Bangalore",
        "destination": "Dubai",
        "departure_date": "2026-10-15",
        "return_date": "2026-10-20",
        "travellers": 1,
        "budget": 80000.0,
        "currency": "INR",
        "cabin_class": "economy",
        "hotel_preference": "3_to_4_star",
    }
    resp = client.post("/travel/plan", headers=headers, json=req_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "trip_id" in data
    assert len(data["flight_options"]) == 3
    assert len(data["hotel_options"]) >= 2
    assert len(data["itinerary"]["days"]) >= 5
    assert data["budget"]["total_projected"] > 0

    trip_id = data["trip_id"]

    # Test retrieval
    get_resp = client.get(f"/travel/plan/{trip_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["trip_id"] == trip_id


def test_flights_search_endpoint():
    req_payload = {
        "origin": "Bangalore",
        "destination": "Dubai",
        "departure_date": "2026-10-15",
        "return_date": "2026-10-20",
        "travellers": 2,
    }
    resp = client.post("/travel/flights/search", headers=headers, json=req_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["flights"]) == 3
    assert data["has_live_gds"] is False


def test_booking_prepare_endpoint_safety():
    # 1. Unconfirmed request
    resp_unconfirmed = client.post(
        "/travel/booking/prepare",
        headers=headers,
        json={
            "trip_id": "trip_test",
            "item_type": "flight",
            "item_id": "fl_1",
            "user_confirmed": False,
        },
    )
    assert resp_unconfirmed.status_code == 200
    data_unconf = resp_unconfirmed.json()
    assert data_unconf["status"] == "rejected"
    assert data_unconf["action_url"] is None

    # 2. Confirmed request
    resp_confirmed = client.post(
        "/travel/booking/prepare",
        headers=headers,
        json={
            "trip_id": "trip_test",
            "item_type": "flight",
            "item_id": "fl_1",
            "user_confirmed": True,
        },
    )
    assert resp_confirmed.status_code == 200
    data_conf = resp_confirmed.json()
    assert data_conf["status"] == "confirmed_redirect"
    assert data_conf["action_url"] is not None

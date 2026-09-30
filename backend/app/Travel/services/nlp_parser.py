"""
Jarvis AIOS — Natural Language Travel Request Parser
---------------------------------------------------
Parses natural language trip requests into strongly typed TripRequest models.
Uses LLM-assisted extraction with a robust zero-failure heuristic fallback.
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.Travel.models.trip_request import TripRequest, NaturalLanguageTripRequest
from app.LLM.client import llm_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Lisa's Travel Extraction Engine.
Extract travel parameters from the user's prompt into a strict JSON object with these keys:
{
  "origin": "City or Airport",
  "destination": "City or Airport",
  "departure_date": "YYYY-MM-DD",
  "return_date": "YYYY-MM-DD",
  "travellers": 1,
  "budget": 80000.0 or null,
  "currency": "INR",
  "cabin_class": "economy",
  "hotel_preference": "3_to_4_star",
  "travel_style": "balanced",
  "activities": ["sightseeing", "food"]
}
Rules:
- If dates are not specified or given as relative durations (e.g. "5-day trip"), assume departure is 14 days from Reference Current Date, and return_date is departure_date + number of days (e.g. 5 days).
- For round trips or vacations, return_date should be departure_date plus trip duration in days.
- Return ONLY raw JSON, no markdown backticks, no conversational text.
"""


def _heuristic_parse(query: str, ref_date: Optional[str] = None) -> TripRequest:
    """Deterministic heuristic and regex extraction for travel prompts."""
    q = query.strip()
    q_lower = q.lower()

    # 1. Dates calculation baseline
    base_date = datetime.now()
    if ref_date:
        try:
            base_date = datetime.strptime(ref_date, "%Y-%m-%d")
        except Exception:
            pass

    # Detect duration in days
    days = 4
    days_match = re.search(r"(\d+)\s*[- ]?(?:day|days|night|nights)", q_lower)
    if days_match:
        days = max(1, min(30, int(days_match.group(1))))

    # Default departure 14 days ahead, return = departure + days
    dep_dt = base_date + timedelta(days=14)
    ret_dt = dep_dt + timedelta(days=days)
    dep_date = dep_dt.strftime("%Y-%m-%d")
    ret_date = ret_dt.strftime("%Y-%m-%d")

    # 2. Extract Route: from X to Y
    origin = "Bangalore"
    destination = "Dubai"

    route_match = re.search(r"(?:from|departs? from)\s+([A-Za-z\s]+?)\s+(?:to|towards?)\s+([A-Za-z\s]+?)(?:\s+under|\s+for|\s+with|\s+in|\s*$|[.,;])", q, re.IGNORECASE)
    if route_match:
        origin = route_match.group(1).strip()
        destination = route_match.group(2).strip()
    else:
        # Check "X to Y"
        simple_route = re.search(r"\b([A-Za-z]+)\s+to\s+([A-Za-z]+)\b", q, re.IGNORECASE)
        if simple_route:
            origin = simple_route.group(1).strip()
            destination = simple_route.group(2).strip()
        else:
            # Check "trip to Y"
            dest_only = re.search(r"(?:trip to|visit|travel to|explore)\s+([A-Za-z]+)", q, re.IGNORECASE)
            if dest_only:
                destination = dest_only.group(1).strip()

    # 3. Extract Budget and Currency
    budget: Optional[float] = None
    currency = "INR"

    # Currency symbols and codes
    if "$" in q or "usd" in q_lower:
        currency = "USD"
    elif "€" in q or "eur" in q_lower:
        currency = "EUR"
    elif "£" in q or "gbp" in q_lower:
        currency = "GBP"
    elif "aed" in q_lower or "dirham" in q_lower:
        currency = "AED"
    else:
        currency = "INR"

    # Match budget: explicit keyword OR currency symbol followed by amount, OR amount followed by currency
    budget_patterns = [
        r"(?:budget(?:\s*of)?|max(?:\s*budget)?|total\s*budget|within|under|below|up\s*to)\s*[:=]?\s*(?:₹|rs\.?|inr|\$|€|£|aed)?\s*([\d,]+(?:\.\d+)?)\s*(?:k|thousand|lakh|lac)?",
        r"(?:₹|rs\.?|inr|\$|€|£|aed)\s*([\d,]+(?:\.\d+)?)\s*(?:k|thousand|lakh|lac)?",
        r"([\d,]+(?:\.\d+)?)\s*(?:k|thousand|lakh|lac)?\s*(?:inr|rs\.?|bucks|usd|eur|gbp|aed|budget)",
    ]
    for pattern in budget_patterns:
        budget_match = re.search(pattern, q_lower)
        if budget_match:
            raw_num = budget_match.group(1).replace(",", "")
            try:
                val = float(raw_num)
                full_match_text = budget_match.group(0).lower()
                if "k" in full_match_text or "thousand" in full_match_text:
                    val *= 1000
                elif "lakh" in full_match_text or "lac" in full_match_text:
                    val *= 100000
                if val >= 100:  # Sensible minimum trip budget
                    budget = val
                    break
            except Exception:
                pass

    # 4. Travellers
    travellers = 1
    pax_match = re.search(r"(\d+)\s*(?:people|persons?|travel{1,2}ers?|adults?|passengers?|pax)", q_lower)
    if pax_match:
        try:
            travellers = max(1, min(20, int(pax_match.group(1))))
        except Exception:
            pass
    elif "couple" in q_lower or "two of us" in q_lower:
        travellers = 2
    elif "family" in q_lower:
        travellers = 4

    # 5. Travel Style
    travel_style = "balanced"
    if "luxury" in q_lower or "5-star" in q_lower:
        travel_style = "luxury"
    elif "budget" in q_lower or "cheap" in q_lower or "backpack" in q_lower:
        travel_style = "relaxed"
    elif "adventure" in q_lower:
        travel_style = "adventure"

    # 6. Cabin class
    cabin = "economy"
    if "business" in q_lower:
        cabin = "business"
    elif "first class" in q_lower:
        cabin = "first"
    elif "premium economy" in q_lower:
        cabin = "premium_economy"

    return TripRequest(
        origin=origin,
        destination=destination,
        departure_date=dep_date,
        return_date=ret_date,
        travellers=travellers,
        budget=budget,
        currency=currency,
        cabin_class=cabin,
        hotel_preference="luxury" if travel_style == "luxury" else "3_to_4_star",
        room_count=max(1, (travellers + 1) // 2),
        travel_style=travel_style,
        activities=[],
        food_preferences=[],
        transport_preferences=["metro", "ride_hail"],
        accessibility_needs=None,
        raw_query=query,
    )


class NaturalLanguageTripParser:
    """Parser coordinating LLM extraction with deterministic heuristic fallback."""

    @classmethod
    def parse_request(cls, req: NaturalLanguageTripRequest) -> TripRequest:
        """Parse natural language query into validated TripRequest."""
        query = req.query.strip()
        ref_date = req.current_date or datetime.now().strftime("%Y-%m-%d")

        try:
            prompt_content = f"Reference Current Date: {ref_date}\nUser Query: {query}"
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_content},
            ]
            response = llm_client.invoke(messages)
            content = getattr(response, "content", "") or str(response)

            # Strip markdown if present
            cleaned = content.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
                cleaned = re.sub(r"\n?```$", "", cleaned)

            data: Dict[str, Any] = json.loads(cleaned.strip())

            # Validate extracted values with fallbacks
            origin = data.get("origin") or "Bangalore"
            destination = data.get("destination") or "Dubai"
            dep_date = data.get("departure_date") or (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            ret_date = data.get("return_date")
            if ret_date in ("null", "None", "", None):
                ret_date = None

            # If return_date was not extracted or null, compute from trip duration in query or default days
            if not ret_date:
                days = 4
                days_match = re.search(r"(\d+)\s*[- ]?(?:day|days|night|nights)", query.lower())
                if days_match:
                    days = max(1, min(30, int(days_match.group(1))))
                try:
                    dep_dt = datetime.strptime(dep_date, "%Y-%m-%d")
                    ret_date = (dep_dt + timedelta(days=days)).strftime("%Y-%m-%d")
                except Exception:
                    pass

            return TripRequest(
                origin=origin,
                destination=destination,
                departure_date=dep_date,
                return_date=ret_date,
                travellers=int(data.get("travellers") or 1),
                budget=float(data["budget"]) if data.get("budget") is not None else None,
                currency=str(data.get("currency") or "INR"),
                cabin_class=str(data.get("cabin_class") or "economy"),
                hotel_preference=str(data.get("hotel_preference") or "3_to_4_star"),
                room_count=max(1, int(data.get("travellers") or 1) // 2 or 1),
                travel_style=str(data.get("travel_style") or "balanced"),
                activities=data.get("activities") or [],
                raw_query=query,
            )

        except Exception as exc:
            logger.warning("[TRAVEL-NLP] LLM extraction fallback to heuristics: %s", exc)
            return _heuristic_parse(query, ref_date)


nlp_parser = NaturalLanguageTripParser()

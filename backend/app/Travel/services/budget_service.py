"""
Jarvis AIOS — Budget Calculation & Itemization Service
------------------------------------------------------
Enforces financial accuracy and transparency:
- Strictly isolates verified prices from estimated spending
- Calculates total projected cost, remaining balance, and budget solvency
- Discloses clear disclaimers so users never mistake estimates for exact quotes
"""

from typing import List, Optional
from app.Travel.models.flight import FlightOption
from app.Travel.models.hotel import HotelOption
from app.Travel.models.transport import RouteGuide
from app.Travel.models.itinerary import Itinerary
from app.Travel.models.budget import BudgetCategory, TripBudget


class BudgetService:
    """Computes comprehensive trip budget breakdown."""

    @classmethod
    def calculate_budget(
        cls,
        user_budget: Optional[float],
        currency: str,
        flight: Optional[FlightOption],
        hotel: Optional[HotelOption],
        route_guide: RouteGuide,
        itinerary: Itinerary,
        travellers: int = 1,
    ) -> TripBudget:
        curr = currency.upper()
        pax = max(1, travellers)

        categories: List[BudgetCategory] = []
        total_verified = 0.0
        total_estimated = 0.0

        # ── 1. FLIGHTS ────────────────────────────────────────────────────────
        flight_cost = flight.price if flight else 0.0
        flight_verified = flight.is_verified if flight else False
        if flight_verified:
            total_verified += flight_cost
        else:
            total_estimated += flight_cost

        categories.append(
            BudgetCategory(
                category="Flights",
                verified_amount=flight_cost if flight_verified else 0.0,
                estimated_amount=flight_cost if not flight_verified else 0.0,
                currency=curr,
                is_verified=flight_verified,
                notes=f"{flight.airline if flight else 'Standard Airfare'} ({pax} traveller{'s' if pax > 1 else ''}, {flight.cabin_class if flight else 'economy'})",
            )
        )

        # ── 2. HOTEL ──────────────────────────────────────────────────────────
        hotel_cost = hotel.total_price if hotel else 0.0
        hotel_verified = hotel.is_verified if hotel else False
        if hotel_verified:
            total_verified += hotel_cost
        else:
            total_estimated += hotel_cost

        categories.append(
            BudgetCategory(
                category="Hotel",
                verified_amount=hotel_cost if hotel_verified else 0.0,
                estimated_amount=hotel_cost if not hotel_verified else 0.0,
                currency=curr,
                is_verified=hotel_verified,
                notes=f"{hotel.name if hotel else 'Accommodation'} ({itinerary.total_days} nights)",
            )
        )

        # ── 3. LOCAL TRANSPORT ────────────────────────────────────────────────
        transport_cost = route_guide.total_estimated_cost
        total_estimated += transport_cost
        categories.append(
            BudgetCategory(
                category="Local transport",
                verified_amount=0.0,
                estimated_amount=transport_cost,
                currency=curr,
                is_verified=False,
                notes="Airport transfers, city metro, and local ride-hail estimates",
            )
        )

        # ── 4. ACTIVITIES & ADMISSIONS ────────────────────────────────────────
        activities_sum = 0.0
        for day in itinerary.days:
            for act in day.activities:
                activities_sum += act.estimated_cost
        total_activities = round(activities_sum * pax, 2)
        total_estimated += total_activities

        categories.append(
            BudgetCategory(
                category="Activities",
                verified_amount=0.0,
                estimated_amount=total_activities,
                currency=curr,
                is_verified=False,
                notes="Sightseeing admissions, observation decks, and tour tickets",
            )
        )

        # ── 5. FOOD & DINING ──────────────────────────────────────────────────
        # Destination dining estimate per person per day
        base_daily_food = 2500.0  # INR approx for international leisure
        if curr == "USD":
            base_daily_food = 35.0
        elif curr == "EUR":
            base_daily_food = 32.0
        elif curr == "AED":
            base_daily_food = 120.0
        elif curr == "GBP":
            base_daily_food = 28.0

        food_total = round(base_daily_food * itinerary.total_days * pax, 2)
        total_estimated += food_total

        categories.append(
            BudgetCategory(
                category="Food",
                verified_amount=0.0,
                estimated_amount=food_total,
                currency=curr,
                is_verified=False,
                notes=f"Breakfast, lunch, and dinner recommendations (~{base_daily_food:.0f} {curr}/day per person)",
            )
        )

        # ── 6. MISCELLANEOUS / CONTINGENCY ────────────────────────────────────
        contingency = round((total_verified + total_estimated) * 0.06, 2)
        total_estimated += contingency

        categories.append(
            BudgetCategory(
                category="Other",
                verified_amount=0.0,
                estimated_amount=contingency,
                currency=curr,
                is_verified=False,
                notes="eSIM / connectivity, tips, local transit card purchase, and emergency buffer (~6%)",
            )
        )

        total_projected = round(total_verified + total_estimated, 2)
        target_budget = user_budget or 0.0
        remaining = round(target_budget - total_projected, 2) if target_budget > 0 else 0.0

        status: str = "unspecified"
        if target_budget > 0:
            status = "within_budget" if remaining >= 0 else "exceeded"

        return TripBudget(
            user_budget=target_budget,
            currency=curr,
            categories=categories,
            total_verified=round(total_verified, 2),
            total_estimated=round(total_estimated, 2),
            total_projected=total_projected,
            remaining_balance=remaining,
            status=status,  # type: ignore
        )


budget_service = BudgetService()

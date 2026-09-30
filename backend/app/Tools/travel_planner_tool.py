"""
Jarvis AIOS — Travel Planner Tool
---------------------------------
Tool Engine wrapper allowing Lisa Assistant to plan trips, compare flights and hotels,
generate multi-day itineraries, calculate budgets, and provide verified booking actions.
"""

from typing import Any, Dict
from app.Tools.tool import Tool
from app.Tools.metadata import ToolMetadata, PermissionLevel
from app.Travel.models.trip_request import NaturalLanguageTripRequest, TripRequest
from app.Travel.services.nlp_parser import nlp_parser
from app.Travel.services.planner_service import planner_service


class TravelPlannerTool(Tool):
    """Integrated Travel Planning Tool for Lisa AIOS."""

    def __init__(self) -> None:
        self.metadata = ToolMetadata(
            name="travel_planner",
            description=(
                "Plan trips, search flights and hotels, construct multi-day itineraries, "
                "calculate budgets, and prepare booking actions with safety controls."
            ),
            permission_level=PermissionLevel.PUBLIC,
        )

    def execute(
        self,
        query: str = "",
        origin: str = "",
        destination: str = "",
        departure_date: str = "",
        return_date: str = "",
        travellers: int = 1,
        budget: float | None = None,
        currency: str = "INR",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute travel planning pipeline."""
        if query and not (origin and destination and departure_date):
            # Parse natural language query
            trip_req = nlp_parser.parse_request(NaturalLanguageTripRequest(query=query))
        else:
            trip_req = TripRequest(
                origin=origin or "Bangalore",
                destination=destination or "Dubai",
                departure_date=departure_date or "2026-10-15",
                return_date=return_date or "2026-10-20",
                travellers=travellers,
                budget=budget,
                currency=currency,
            )

        plan = planner_service.create_travel_plan(trip_req)

        # Build readable markdown response for Assistant
        flight_lines = []
        for f in plan.flight_options:
            flight_lines.append(
                f"- **{f.category.title()}**: {f.airline} — {f.price:,.0f} {f.currency} ({f.duration_minutes // 60}h {f.duration_minutes % 60}m, {f.stops} stops). *{f.rationale}* [Check Fare]({f.deep_link})"
            )

        hotel_lines = []
        for h in plan.hotel_options[:3]:
            hotel_lines.append(
                f"- **{h.name}** ({h.star_rating}★, {h.user_rating}/10): {h.price_per_night:,.0f} {h.currency}/night (Total: {h.total_price:,.0f} {h.currency}). *{h.rationale}* [View Property]({h.booking_url})"
            )

        itinerary_lines = []
        for day in plan.itinerary.days[:3]:
            acts = ", ".join(a.title for a in day.activities)
            itinerary_lines.append(f"- **Day {day.day_number}** ({day.theme}): {acts}")
        if len(plan.itinerary.days) > 3:
            itinerary_lines.append(f"- *...and {len(plan.itinerary.days) - 3} more days in the complete itinerary.*")

        markdown_summary = (
            f"### ✈️ {plan.title}\n\n"
            f"{plan.summary}\n\n"
            f"#### 🛫 Flight Choices (Verified Aggregator Links)\n"
            + "\n".join(flight_lines) + "\n\n"
            "#### 🏨 Accommodations\n"
            + "\n".join(hotel_lines) + "\n\n"
            "#### 📅 Daily Itinerary Outline\n"
            + "\n".join(itinerary_lines) + "\n\n"
            f"#### 💰 Budget Status: {plan.budget.status.replace('_', ' ').title()}\n"
            f"- **Target Budget**: {plan.budget.user_budget:,.0f} {plan.budget.currency}\n"
            f"- **Projected Total**: {plan.budget.total_projected:,.0f} {plan.budget.currency} "
            f"({plan.budget.remaining_balance:+,.0f} balance)\n\n"
            f"👉 **[Open Interactive Travel Planner](/travel?trip_id={plan.trip_id})** to explore day-by-day maps, adjust pacing, or review bookings."
        )

        return {
            "status": "success",
            "trip_id": plan.trip_id,
            "title": plan.title,
            "summary": markdown_summary,
            "plan": plan.model_dump(),
        }

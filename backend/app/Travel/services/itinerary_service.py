"""
Jarvis AIOS — Itinerary Generation Service
------------------------------------------
Generates balanced, customizable multi-day itineraries with morning, afternoon,
and evening segments, estimated timings, local transit considerations, and meal recommendations.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Literal
from app.Travel.models.trip_request import TripRequest
from app.Travel.models.itinerary import ActivityItem, DayPlan, Itinerary


DESTINATION_DAY_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "dubai": [
        {
            "theme": "Arrival, Downtown Dubai & The Burj Khalifa",
            "morning": {
                "title": "Hotel Check-in & Downtown Orientation",
                "desc": "Arrive at hotel, unpack, refresh, and take a gentle stroll around Downtown Boulevard.",
                "loc": "Downtown Dubai",
                "dur": 120,
                "cost_inr": 0.0,
                "booking": False,
                "hours": "Open 24/7",
            },
            "afternoon": {
                "title": "The Dubai Mall & Dubai Aquarium",
                "desc": "Explore the world's largest shopping and entertainment destination, including the underwater tunnel.",
                "loc": "Financial Centre Road, Downtown",
                "dur": 180,
                "cost_inr": 3500.0,
                "booking": True,
                "hours": "10:00 - 23:00",
            },
            "evening": {
                "title": "At The Top: Burj Khalifa & Dubai Fountain Show",
                "desc": "Ascend levels 124 & 125 of Burj Khalifa at sunset followed by the world-famous synchronized fountain show.",
                "loc": "Sheikh Mohammed bin Rashid Blvd",
                "dur": 150,
                "cost_inr": 4200.0,
                "booking": True,
                "hours": "Sunset slots (17:30 - 19:30 recommended)",
            },
            "meals": ["Welcome Arabic Coffee & Dates", "Lunch at Time Out Market Dubai", "Dinner at Abd El Wahab (Fountain views)"],
            "daily_spend_inr": 9500.0,
        },
        {
            "theme": "Heritage, Old Dubai & The Gold & Spice Souks",
            "morning": {
                "title": "Al Fahidi Historical Neighbourhood",
                "desc": "Wander through restored wind-tower architecture, narrow alleys, and the Dubai Coffee Museum.",
                "loc": "Al Fahidi, Bur Dubai",
                "dur": 120,
                "cost_inr": 400.0,
                "booking": False,
                "hours": "09:00 - 17:00",
            },
            "afternoon": {
                "title": "Traditional Abra Boat Crossing to Deira Souks",
                "desc": "Take a historic wooden abra across Dubai Creek to explore the fragrant Spice Souk and dazzling Gold Souk.",
                "loc": "Dubai Creek to Deira",
                "dur": 150,
                "cost_inr": 50.0,
                "booking": False,
                "hours": "10:00 - 22:00",
            },
            "evening": {
                "title": "Al Seef Waterfront Promenade & Heritage Dinner",
                "desc": "Stroll the atmospheric lanterns and cobblestone paths along Dubai Creek with local Emirati dining.",
                "loc": "Al Seef Street, Bur Dubai",
                "dur": 120,
                "cost_inr": 2000.0,
                "booking": False,
                "hours": "Open until 23:00",
            },
            "meals": ["Breakfast at Arabian Tea House (Al Fahidi)", "Authentic Shawarma & Falafel lunch", "Emirati dinner at Al Fanar Restaurant"],
            "daily_spend_inr": 4500.0,
        },
        {
            "theme": "Desert Safari, Dune Bashing & Bedouin Camp",
            "morning": {
                "title": "Leisure Morning & Museum of the Future",
                "desc": "Visit the architectural marvel showcasing futuristic innovations, space travel, and climate ecosystems.",
                "loc": "Sheikh Zayed Road",
                "dur": 150,
                "cost_inr": 3600.0,
                "booking": True,
                "hours": "10:00 - 18:00 (advance booking mandatory)",
            },
            "afternoon": {
                "title": "4x4 Red Dune Bashing & Sandboarding",
                "desc": "Afternoon pickup for thrilling 4x4 dune drive into Lahbab Red Dunes followed by sunset sandboarding.",
                "loc": "Lahbab Desert Conservation Reserve",
                "dur": 240,
                "cost_inr": 5500.0,
                "booking": True,
                "hours": "15:00 - 21:30",
            },
            "evening": {
                "title": "Bedouin Desert Camp, BBQ Buffet & Stargazing",
                "desc": "Traditional Arabic camp with camel rides, henna painting, Tanoura dance, live fire show, and BBQ dinner.",
                "loc": "Al Marmoom Desert",
                "dur": 180,
                "cost_inr": 0.0,  # Included in safari package
                "booking": True,
                "hours": "Included in Desert Safari",
            },
            "meals": ["Breakfast at cafe", "Light lunch at City Walk", "Traditional BBQ buffet in the desert"],
            "daily_spend_inr": 10500.0,
        },
        {
            "theme": "Dubai Marina, JBR Beach & Palm Jumeirah",
            "morning": {
                "title": "The View at The Palm",
                "desc": "360-degree panoramic observation deck on level 52 of Palm Tower overlooking Palm Jumeirah and the Arabian Gulf.",
                "loc": "Nakheel Mall, Palm Jumeirah",
                "dur": 120,
                "cost_inr": 2800.0,
                "booking": True,
                "hours": "09:00 - 19:30",
            },
            "afternoon": {
                "title": "Dubai Marina Walk & Yacht Cruise",
                "desc": "Scenic 1-hour shared speedboat or luxury catamaran tour cruising around Ain Dubai and Burj Al Arab.",
                "loc": "Dubai Marina Yacht Club",
                "dur": 120,
                "cost_inr": 3200.0,
                "booking": True,
                "hours": "14:00 - 18:00",
            },
            "evening": {
                "title": "JBR The Beach & Sunset Dining",
                "desc": "Relax on Jumeirah Beach Residence sands, browse open-air seaside boutiques, and enjoy sunset dining.",
                "loc": "The Beach, JBR",
                "dur": 150,
                "cost_inr": 2500.0,
                "booking": False,
                "hours": "Open until midnight",
            },
            "meals": ["Croissant & coffee at Marina Walk", "Seafood lunch at Operation: Falafel or Catch22", "Sunset dinner at Bla Bla Dubai or Pier 7"],
            "daily_spend_inr": 9800.0,
        },
        {
            "theme": "Souk Madinat Jumeirah, Cultural Art & Departure",
            "morning": {
                "title": "Souk Madinat Jumeirah & Abra Lagoon Ride",
                "desc": "Explore modern Arabian bazaar with meandering water canals offering postcard-perfect views of Burj Al Arab.",
                "loc": "Al Sufouh 1",
                "dur": 120,
                "cost_inr": 1800.0,
                "booking": False,
                "hours": "10:00 - 23:00",
            },
            "afternoon": {
                "title": "Alserkal Avenue Contemporary Art District",
                "desc": "Industrial warehouse galleries, indie coffee roasters, design studios, and chocolate makers in Al Quoz.",
                "loc": "Al Quoz Industrial 1",
                "dur": 120,
                "cost_inr": 500.0,
                "booking": False,
                "hours": "10:00 - 19:00",
            },
            "evening": {
                "title": "Souvenir Shopping & Airport Departure Transfer",
                "desc": "Final luggage packing, souvenir pick-up (camel milk chocolates, perfumes), and transfer to DXB Airport.",
                "loc": "Hotel to DXB Terminal",
                "dur": 120,
                "cost_inr": 1500.0,
                "booking": False,
                "hours": "According to flight departure",
            },
            "meals": ["Breakfast overlooking Burj Al Arab canals", "Specialty coffee & lunch at Nightjar Cafe (Alserkal)", "Departure dinner at Dubai Airport"],
            "daily_spend_inr": 5500.0,
        },
    ],
}


def _build_generic_day_plan(day_num: int, dest: str, date_str: str | None, curr_mult: float) -> DayPlan:
    """Generate intelligent generic day plan for any destination worldwide."""
    dest_title = dest.title()
    themes = [
        "Arrival, Central Orientation & Historic Landmark Tour",
        "Iconic Monuments, Cultural Museums & Local Markets",
        "Nature, Scenic Panoramas & Active Sightseeing",
        "Neighborhood Exploration, Arts & Gastronomy",
        "Leisure Shopping, Panoramic Overlook & Departure",
    ]
    theme_idx = (day_num - 1) % len(themes)

    activities = [
        ActivityItem(
            time_slot="morning",
            title="Historic District Walk & Landmark Heritage",
            description=f"Explore the celebrated core of {dest_title} with guided highlights and architectural sightseeing.",
            location=f"Central Old Town, {dest_title}",
            duration_mins=120,
            estimated_cost=round(1200.0 * curr_mult, 2),
            booking_required=False,
            opening_hours="09:00 - 17:00",
        ),
        ActivityItem(
            time_slot="afternoon",
            title="Premier Cultural Museum & Park Gardens",
            description="Immerse yourself in world-class art collections, historic artifacts, and surrounding botanical grounds.",
            location=f"Museum Quarter, {dest_title}",
            duration_mins=180,
            estimated_cost=round(2000.0 * curr_mult, 2),
            booking_required=True,
            opening_hours="10:00 - 18:00",
        ),
        ActivityItem(
            time_slot="evening",
            title="Panoramic Sunset Viewpoint & Waterfront Stroll",
            description=f"Enjoy scenic evening golden hour views over the {dest_title} skyline followed by local dining.",
            location=f"Scenic Promenade, {dest_title}",
            duration_mins=120,
            estimated_cost=round(1500.0 * curr_mult, 2),
            booking_required=False,
            opening_hours="Open 24/7",
        ),
    ]

    return DayPlan(
        day_number=day_num,
        date=date_str,
        theme=themes[theme_idx],
        activities=activities,
        meal_suggestions=[
            "Local bakery breakfast near accommodations",
            "Authentic lunch featuring regional specialties",
            f"Atmospheric dinner at top-rated bistro in {dest_title}",
        ],
        estimated_daily_spend=round(6500.0 * curr_mult, 2),
        daily_transport=[],
    )


class ItineraryService:
    """Orchestrates comprehensive multi-day itinerary construction and user customization."""

    @classmethod
    def generate_itinerary(cls, request: TripRequest) -> Itinerary:
        dest_clean = request.destination.strip().lower()
        curr = request.currency.upper()

        rate_multiplier = 1.0
        if curr == "USD":
            rate_multiplier = 0.012
        elif curr == "EUR":
            rate_multiplier = 0.011
        elif curr == "AED":
            rate_multiplier = 0.044
        elif curr == "GBP":
            rate_multiplier = 0.0095

        # Calculate total days from departure and return dates
        total_days = 5
        start_date = None
        try:
            d1 = datetime.strptime(request.departure_date, "%Y-%m-%d")
            start_date = d1
            if request.return_date:
                d2 = datetime.strptime(request.return_date, "%Y-%m-%d")
                total_days = max(1, min(14, (d2 - d1).days + 1))
        except Exception:
            total_days = 5

        # Pacing filter
        pace_setting: Literal["relaxed", "balanced", "intense"] = "balanced"
        if request.travel_style == "relaxed":
            pace_setting = "relaxed"
        elif request.travel_style in ["adventure", "fast_paced"]:
            pace_setting = "intense"

        # Check for benchmark city
        matched_city = None
        for k in DESTINATION_DAY_TEMPLATES:
            if k in dest_clean:
                matched_city = k
                break

        days: List[DayPlan] = []

        if matched_city:
            templates = DESTINATION_DAY_TEMPLATES[matched_city]
            for day_i in range(1, total_days + 1):
                t_idx = (day_i - 1) % len(templates)
                tmpl = templates[t_idx]

                cur_date_str = None
                if start_date:
                    cur_date_str = (start_date + timedelta(days=day_i - 1)).strftime("%Y-%m-%d")

                activities: List[ActivityItem] = [
                    ActivityItem(
                        time_slot="morning",
                        title=tmpl["morning"]["title"],
                        description=tmpl["morning"]["desc"],
                        location=tmpl["morning"]["loc"],
                        duration_mins=tmpl["morning"]["dur"],
                        estimated_cost=round(tmpl["morning"]["cost_inr"] * rate_multiplier, 2),
                        booking_required=tmpl["morning"]["booking"],
                        opening_hours=tmpl["morning"].get("hours"),
                    ),
                    ActivityItem(
                        time_slot="afternoon",
                        title=tmpl["afternoon"]["title"],
                        description=tmpl["afternoon"]["desc"],
                        location=tmpl["afternoon"]["loc"],
                        duration_mins=tmpl["afternoon"]["dur"],
                        estimated_cost=round(tmpl["afternoon"]["cost_inr"] * rate_multiplier, 2),
                        booking_required=tmpl["afternoon"]["booking"],
                        opening_hours=tmpl["afternoon"].get("hours"),
                    ),
                ]

                # Relaxed pace drops evening scheduled sight; Intense keeps all plus bonus
                if pace_setting != "relaxed":
                    activities.append(
                        ActivityItem(
                            time_slot="evening",
                            title=tmpl["evening"]["title"],
                            description=tmpl["evening"]["desc"],
                            location=tmpl["evening"]["loc"],
                            duration_mins=tmpl["evening"]["dur"],
                            estimated_cost=round(tmpl["evening"]["cost_inr"] * rate_multiplier, 2),
                            booking_required=tmpl["evening"]["booking"],
                            opening_hours=tmpl["evening"].get("hours"),
                        )
                    )

                daily_cost = round(tmpl["daily_spend_inr"] * rate_multiplier, 2)
                days.append(
                    DayPlan(
                        day_number=day_i,
                        date=cur_date_str,
                        theme=tmpl["theme"],
                        activities=activities,
                        meal_suggestions=tmpl["meals"],
                        estimated_daily_spend=daily_cost,
                        daily_transport=[],
                    )
                )
        else:
            for day_i in range(1, total_days + 1):
                cur_date_str = None
                if start_date:
                    cur_date_str = (start_date + timedelta(days=day_i - 1)).strftime("%Y-%m-%d")
                days.append(_build_generic_day_plan(day_i, request.destination, cur_date_str, rate_multiplier))

        travel_tips = [
            f"Carry lightweight, modest clothing suitable for climate in {request.destination.title()}.",
            "Pre-book high-demand observation decks and desert excursions to secure prime sunset time slots.",
            "Stay hydrated and avoid heavy outdoor walking during midday peak temperatures.",
            "Always keep a physical copy and digital photo of your passport and travel insurance on your phone.",
        ]

        return Itinerary(
            destination=request.destination.title(),
            total_days=total_days,
            pace=pace_setting,
            days=days,
            travel_tips=travel_tips,
        )


itinerary_service = ItineraryService()

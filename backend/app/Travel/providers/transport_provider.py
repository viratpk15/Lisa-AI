"""
Jarvis AIOS — Local Transport & Transit Provider
------------------------------------------------
Generates sequential transit segments connecting Airport, Hotel, and Sightseeing clusters.
Provides deep-links for ride-hailing (Uber/Careem) and official transit authorities.
Zero-fabrication: Never claims a cab or ticket was booked without real provider API confirmation.
"""

from typing import List
from app.Travel.models.transport import TransportSegment, RouteGuide
from app.Travel.providers.base import BaseTransportProvider


class LocalTransportProvider(BaseTransportProvider):
    """Generates verified local transit recommendations and route guides."""

    def get_transport_segments(
        self,
        origin_city: str,
        destination_city: str,
        hotel_name: str,
        attractions: List[str],
        currency: str = "INR",
    ) -> List[TransportSegment]:
        dest_clean = destination_city.strip().lower()
        curr = currency.upper()

        # Currency conversion multiplier from INR
        rate_multiplier = 1.0
        if curr == "USD":
            rate_multiplier = 0.012
        elif curr == "EUR":
            rate_multiplier = 0.011
        elif curr == "AED":
            rate_multiplier = 0.044
        elif curr == "GBP":
            rate_multiplier = 0.0095

        segments: List[TransportSegment] = []

        # ── 1. AIRPORT TO HOTEL ──────────────────────────────────────────────
        airport_name = f"{destination_city.title()} International Airport"
        if "dubai" in dest_clean:
            airport_name = "Dubai International Airport (DXB)"
            metro_cost = round(120.0 * rate_multiplier, 2)
            taxi_cost = round(1800.0 * rate_multiplier, 2)

            segments.append(
                TransportSegment(
                    segment_id="seg_airport_arrival_metro",
                    from_name=airport_name,
                    to_name=hotel_name,
                    mode="metro",
                    estimated_duration_mins=25,
                    estimated_cost=metro_cost,
                    currency=curr,
                    is_verified=False,
                    provider_name="Dubai Metro (Red Line)",
                    notes="Direct Red Line from Terminal 1 & 3 to Downtown / Business Bay. Use Nol Silver card.",
                    deep_link="https://www.rta.ae/wps/portal/rta/ae/public-transport/metro",
                )
            )
            segments.append(
                TransportSegment(
                    segment_id="seg_airport_arrival_taxi",
                    from_name=airport_name,
                    to_name=hotel_name,
                    mode="ride_hail",
                    estimated_duration_mins=20,
                    estimated_cost=taxi_cost,
                    currency=curr,
                    is_verified=False,
                    provider_name="Dubai Taxi (DTC) / Careem",
                    notes="Official metered airport taxis available 24/7 at all terminal arrival ranks.",
                    deep_link="https://m.uber.com/ul/?action=setPickup",
                )
            )
        elif "london" in dest_clean:
            airport_name = "London Heathrow Airport (LHR)"
            segments.append(
                TransportSegment(
                    segment_id="seg_airport_arrival_rail",
                    from_name=airport_name,
                    to_name=hotel_name,
                    mode="train",
                    estimated_duration_mins=30,
                    estimated_cost=round(2400.0 * rate_multiplier, 2),
                    currency=curr,
                    is_verified=False,
                    provider_name="Elizabeth Line / Heathrow Express",
                    notes="Fast modern connection directly into central London (Paddington / Liverpool St).",
                    deep_link="https://tfl.gov.uk/fares/",
                )
            )
        else:
            segments.append(
                TransportSegment(
                    segment_id="seg_airport_arrival_taxi",
                    from_name=airport_name,
                    to_name=hotel_name,
                    mode="taxi",
                    estimated_duration_mins=35,
                    estimated_cost=round(1500.0 * rate_multiplier, 2),
                    currency=curr,
                    is_verified=False,
                    provider_name="Airport Taxi Rank / Ride-Hail",
                    notes="Official airport taxi stands available outside main arrivals hall.",
                    deep_link="https://m.uber.com/ul/?action=setPickup",
                )
            )

        # ── 2. DAILY ATTRACTION TRANSIT ──────────────────────────────────────
        primary_attraction = attractions[0] if attractions else f"Historic Core, {destination_city.title()}"
        segments.append(
            TransportSegment(
                segment_id="seg_daily_sightseeing",
                from_name=hotel_name,
                to_name=primary_attraction,
                mode="metro" if "dubai" in dest_clean or "london" in dest_clean else "ride_hail",
                estimated_duration_mins=15,
                estimated_cost=round(250.0 * rate_multiplier, 2),
                currency=curr,
                is_verified=False,
                provider_name="Local Transit / City Metro",
                notes="Recommended for scenic transit avoiding peak road traffic.",
                deep_link="https://m.uber.com/ul/?action=setPickup",
            )
        )

        # ── 3. HOTEL TO AIRPORT RETURN ───────────────────────────────────────
        segments.append(
            TransportSegment(
                segment_id="seg_departure_transfer",
                from_name=hotel_name,
                to_name=airport_name,
                mode="ride_hail",
                estimated_duration_mins=30,
                estimated_cost=round(1600.0 * rate_multiplier, 2),
                currency=curr,
                is_verified=False,
                provider_name="Scheduled Airport Cab / Ride-Hail",
                notes="Depart hotel at least 3.5 hours prior to international departure.",
                deep_link="https://m.uber.com/ul/?action=setPickup",
            )
        )

        return segments

    def generate_route_guide(
        self,
        origin_city: str,
        destination_city: str,
        hotel_name: str,
        attractions: List[str],
        currency: str = "INR",
    ) -> RouteGuide:
        """Construct route guide with preparation essentials."""
        segments = self.get_transport_segments(origin_city, destination_city, hotel_name, attractions, currency)
        total_transit_cost = sum(s.estimated_cost for s in segments if "taxi" in s.mode or "ride_hail" in s.mode or "train" in s.mode)

        dest_clean = destination_city.strip().lower()
        prep_items = [
            "Check passport validity (must have at least 6 months validity from departure date).",
            f"Review visa requirements for travel between {origin_city.title()} and {destination_city.title()}.",
            "Pre-purchase an international travel eSIM or local SIM card for real-time navigation.",
            "Notify your bank of international debit/credit card usage to prevent fraud freezes.",
            "Carry a universal travel adapter plug compatible with destination power sockets.",
        ]

        if "dubai" in dest_clean:
            prep_items.extend([
                "Purchase a Nol Silver Card at Dubai Airport Metro station for all bus, metro, and tram trips.",
                "Download the Careem app (works across Dubai for taxis, food, and bike rentals).",
                "Dress respectfully when visiting traditional neighborhoods and religious sites.",
            ])
        elif "london" in dest_clean:
            prep_items.extend([
                "TfL accepts contactless bank cards and Apple/Google Pay on all Tube lines and buses (no Oyster card needed).",
                "Pack a compact umbrella and weather-resistant walking shoes.",
            ])

        return RouteGuide(
            segments=segments,
            total_estimated_cost=round(total_transit_cost, 2),
            currency=currency.upper(),
            preparation_items=prep_items,
        )


transport_provider = LocalTransportProvider()

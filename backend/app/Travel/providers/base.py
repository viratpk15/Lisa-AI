"""
Jarvis AIOS — Travel Provider Base Abstractions
"""

from abc import ABC, abstractmethod
from typing import List
from app.Travel.models.trip_request import TripRequest
from app.Travel.models.flight import FlightOption
from app.Travel.models.hotel import HotelOption
from app.Travel.models.transport import TransportSegment


class BaseFlightProvider(ABC):
    """Abstract interface for flight search providers."""

    @abstractmethod
    def search_flights(self, request: TripRequest) -> List[FlightOption]:
        """Search and categorize flight options."""
        pass


class BaseHotelProvider(ABC):
    """Abstract interface for accommodation search providers."""

    @abstractmethod
    def search_hotels(self, request: TripRequest) -> List[HotelOption]:
        """Search accommodation options for requested destination and dates."""
        pass


class BaseTransportProvider(ABC):
    """Abstract interface for local transportation routing."""

    @abstractmethod
    def get_transport_segments(
        self,
        origin_city: str,
        destination_city: str,
        hotel_name: str,
        attractions: List[str],
        currency: str,
    ) -> List[TransportSegment]:
        """Generate structured route segments between airport, hotel, and attractions."""
        pass

"""
Jarvis AIOS — Weather Data Validator
-------------------------------------

Validates weather forecast data (Open-Meteo, IMD, AccuWeather).
"""

import logging
from typing import Tuple
from app.Tools.live_information.validators.base import BaseLiveValidator

logger = logging.getLogger(__name__)

TRUSTED_WEATHER_SOURCES = [
    "open-meteo", "imd", "accuweather", "weather.com", "noaa", "met office",
    "duckduckgo", "open-meteo weather api"
]


class WeatherValidator(BaseLiveValidator):
    """Domain validator for weather forecasts."""

    def validate(self, payload: dict, source: str) -> Tuple[bool, float, str]:
        if not payload:
            return False, 0.0, "Empty payload"

        temp = payload.get("temperature_celsius")
        location = payload.get("location")

        if temp is None or not location:
            return False, 0.0, "Missing required fields (temperature_celsius, location)"

        try:
            temp_val = float(temp)
        except (ValueError, TypeError):
            return False, 0.0, f"Invalid numeric temperature format: {temp}"

        # Real temperature bounds on Earth: -90°C to +60°C
        if not (-90.0 <= temp_val <= 60.0):
            return False, 0.0, f"Temperature out of Earth atmospheric bounds: {temp_val}°C"

        source_lower = source.lower()
        is_trusted = any(ts in source_lower for ts in TRUSTED_WEATHER_SOURCES)
        confidence = 0.98 if is_trusted else 0.85

        return True, confidence, f"Validated weather payload ({location} {temp_val}°C)"

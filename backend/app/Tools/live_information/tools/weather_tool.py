"""
Jarvis AIOS — Live Weather Tool
-------------------------------

Fetches live weather forecasts via Open-Meteo API or fallback,
validates through WeatherValidator, and returns ToolResult.
"""

import json
import logging
import urllib.request
from datetime import datetime, timezone

from app.Tools.live_information.contracts import ToolResult
from app.Tools.live_information.validators.weather_validator import WeatherValidator

logger = logging.getLogger(__name__)


class WeatherTool:
    """Tool for fetching and validating live weather data."""

    def __init__(self) -> None:
        self.validator = WeatherValidator()

    def execute(self, query: str) -> ToolResult:
        logger.info("[WEATHER-TOOL] Executing weather fetch for query='%s'", query)
        location = "Channapatna"
        lat, lon = 12.6518, 77.2084

        try:
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                f"&current_weather=true&hourly=precipitation_probability,temperature_2m"
            )
            req = urllib.request.Request(weather_url, headers={"User-Agent": "JarvisAIOS/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                curr = data.get("current_weather", {})
                temp = curr.get("temperature")
                wind = curr.get("windspeed", 0.0)
                prob = data.get("hourly", {}).get("precipitation_probability", [0])[0]

                payload = {
                    "location": location,
                    "temperature_celsius": temp,
                    "wind_speed_kmh": wind,
                    "precipitation_probability_percent": prob,
                    "formatted_string": f"Temperature: {temp}°C, Wind: {wind} km/h, Rain Probability: {prob}%",
                }
                source = "Open-Meteo Weather API"

                is_valid, confidence, reason = self.validator.validate(payload, source)
                if not is_valid or confidence < 0.8:
                    return ToolResult(
                        success=True,
                        verified=False,
                        confidence=confidence,
                        source=source,
                        payload=payload,
                        error=f"Weather validation failed: {reason}",
                    )

                return ToolResult(
                    success=True,
                    verified=True,
                    confidence=confidence,
                    source=source,
                    timestamp=datetime.now(timezone.utc),
                    payload=payload,
                )
        except Exception as e:
            logger.error("[WEATHER-TOOL] Fetch error: %s", str(e))
            return ToolResult(
                success=False,
                verified=False,
                confidence=0.0,
                source="Open-Meteo",
                error=f"Weather API request failed: {str(e)}",
            )

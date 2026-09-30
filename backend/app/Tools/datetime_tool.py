import re
from datetime import datetime
from typing import Any
import zoneinfo

from app.Tools.tool import Tool

_CITY_TIMEZONE_MAP: dict[str, str] = {
    "tokyo": "Asia/Tokyo",
    "japan": "Asia/Tokyo",
    "delhi": "Asia/Kolkata",
    "new delhi": "Asia/Kolkata",
    "bengaluru": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata",
    "kolkata": "Asia/Kolkata",
    "chennai": "Asia/Kolkata",
    "india": "Asia/Kolkata",
    "london": "Europe/London",
    "uk": "Europe/London",
    "united kingdom": "Europe/London",
    "new york": "America/New_York",
    "nyc": "America/New_York",
    "san francisco": "America/Los_Angeles",
    "los angeles": "America/Los_Angeles",
    "california": "America/Los_Angeles",
    "seattle": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "paris": "Europe/Paris",
    "france": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "germany": "Europe/Berlin",
    "amsterdam": "Europe/Amsterdam",
    "rome": "Europe/Rome",
    "italy": "Europe/Rome",
    "dubai": "Asia/Dubai",
    "uae": "Asia/Dubai",
    "singapore": "Asia/Singapore",
    "hong kong": "Asia/Hong_Kong",
    "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",
    "australia": "Australia/Sydney",
    "toronto": "America/Toronto",
    "canada": "America/Toronto",
    "utc": "UTC",
    "gmt": "UTC",
}


class DateTimeTool(Tool):
    name = "datetime"

    description = "Returns the current date and time, optionally for a specific timezone or city."

    def execute(self, **kwargs: Any) -> Any:
        query = str(kwargs.get("query") or "").lower()
        location = str(kwargs.get("location") or kwargs.get("timezone") or "").lower()

        target_tz_name: str | None = None
        matched_city: str | None = None

        search_text = f"{location} {query}".strip()
        if search_text:
            # Check known city/country mapping
            for city, tz_name in _CITY_TIMEZONE_MAP.items():
                if re.search(r"\b" + re.escape(city) + r"\b", search_text):
                    target_tz_name = tz_name
                    matched_city = city.title()
                    break

            # Try direct IANA timezone if not matched by city
            if not target_tz_name and location:
                try:
                    zoneinfo.ZoneInfo(location)
                    target_tz_name = location
                except Exception:
                    pass

        if target_tz_name:
            try:
                tz = zoneinfo.ZoneInfo(target_tz_name)
                now_in_tz = datetime.now(tz)
                city_label = f"in {matched_city} " if matched_city else f"in {target_tz_name} "
                return (
                    f"The current date and time {city_label}is {now_in_tz.strftime('%A, %B %d, %Y at %I:%M:%S %p')} "
                    f"({target_tz_name}, UTC{now_in_tz.strftime('%z')})."
                )
            except Exception:
                pass

        # Default: current local system datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


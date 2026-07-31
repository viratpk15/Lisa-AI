"""
Jarvis AIOS — Forex Data Validator
----------------------------------

Validates foreign exchange currency rates (USD-INR, EUR-USD, etc.).
"""

import logging
from typing import Tuple
from app.Tools.live_information.validators.base import BaseLiveValidator

logger = logging.getLogger(__name__)

TRUSTED_FOREX_SOURCES = [
    "rbi", "xe", "oanda", "yahoo finance", "google finance", "bloomberg", "reuters"
]


class ForexValidator(BaseLiveValidator):
    """Domain validator for foreign exchange rates."""

    def validate(self, payload: dict, source: str) -> Tuple[bool, float, str]:
        if not payload:
            return False, 0.0, "Empty payload"

        rate = payload.get("rate")
        base = payload.get("base_currency")
        target = payload.get("target_currency")

        if rate is None or not base or not target:
            return False, 0.0, "Missing required fields (rate, base_currency, target_currency)"

        try:
            rate_val = float(rate)
        except (ValueError, TypeError):
            return False, 0.0, f"Invalid numeric exchange rate format: {rate}"

        if rate_val <= 0:
            return False, 0.0, f"Non-positive exchange rate: {rate_val}"

        source_lower = source.lower()
        is_trusted = any(ts in source_lower for ts in TRUSTED_FOREX_SOURCES)
        confidence = 0.95 if is_trusted else 0.85

        return True, confidence, f"Validated forex payload ({base}/{target} {rate_val})"

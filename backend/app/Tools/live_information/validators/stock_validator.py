"""
Jarvis AIOS — Stock Market Validator
-------------------------------------

Validates stock price, market indices (NSE, BSE, S&P 500), gainers/losers.
"""

import logging
from typing import Tuple
from app.Tools.live_information.validators.base import BaseLiveValidator

logger = logging.getLogger(__name__)

TRUSTED_STOCK_SOURCES = [
    "nse", "bse", "moneycontrol", "yahoo finance", "google finance",
    "bloomberg", "reuters", "economic times", "business standard", "livemint"
]


class StockValidator(BaseLiveValidator):
    """Domain validator for stock market prices, indices, and financial market queries."""

    def validate(self, payload: dict, source: str) -> Tuple[bool, float, str]:
        if not payload:
            return False, 0.0, "Empty payload"

        symbol = str(payload.get("symbol") or payload.get("asset") or "").strip()
        price = payload.get("price_numeric")

        if not symbol or price is None:
            return False, 0.0, "Missing required fields (symbol/asset, price_numeric)"

        try:
            price_val = float(price)
        except (ValueError, TypeError):
            return False, 0.0, f"Invalid numeric price format: {price}"

        if price_val <= 0:
            return False, 0.0, f"Non-positive stock price/index value: {price_val}"

        source_lower = source.lower()
        is_trusted = any(ts in source_lower for ts in TRUSTED_STOCK_SOURCES)
        confidence = 0.95 if is_trusted else 0.85

        return True, confidence, f"Validated stock payload ({symbol} {price_val})"

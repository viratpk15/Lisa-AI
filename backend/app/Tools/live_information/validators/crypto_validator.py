"""
Jarvis AIOS — Crypto Data Validator
-----------------------------------

Validates cryptocurrency market data (BTC, ETH, SOL, etc.).
"""

import logging
from typing import Tuple
from app.Tools.live_information.validators.base import BaseLiveValidator

logger = logging.getLogger(__name__)

TRUSTED_CRYPTO_SOURCES = [
    "coinmarketcap", "coingecko", "binance", "coinbase", "yahoo finance",
    "reuters", "bloomberg", "tradingview"
]


class CryptoValidator(BaseLiveValidator):
    """Domain validator for cryptocurrency prices."""

    def validate(self, payload: dict, source: str) -> Tuple[bool, float, str]:
        if not payload:
            return False, 0.0, "Empty payload"

        asset = str(payload.get("asset") or payload.get("symbol") or "").strip()
        price = payload.get("price_numeric")

        if not asset or price is None:
            return False, 0.0, "Missing required fields (asset/symbol, price_numeric)"

        try:
            price_val = float(price)
        except (ValueError, TypeError):
            return False, 0.0, f"Invalid numeric price format: {price}"

        if price_val <= 0:
            return False, 0.0, f"Non-positive crypto price: {price_val}"

        source_lower = source.lower()
        is_trusted = any(ts in source_lower for ts in TRUSTED_CRYPTO_SOURCES)
        confidence = 0.95 if is_trusted else 0.85

        return True, confidence, f"Validated crypto payload ({asset} ${price_val})"

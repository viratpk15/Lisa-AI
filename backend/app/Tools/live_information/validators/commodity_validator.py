"""
Jarvis AIOS — Commodity Validator
---------------------------------

Validates commodity payloads (Gold, Silver, Platinum, Spot Metals).
Checks:
  - Required fields (asset, price_numeric, unit, currency)
  - Unit sanity and mathematical conversion consistency
  - Trusted source verification
"""

import logging
from typing import Tuple
from app.Tools.live_information.validators.base import BaseLiveValidator

logger = logging.getLogger(__name__)

# Trusted sources whitelist for commodities
TRUSTED_COMMODITY_SOURCES = [
    "ibja", "mcx", "moneycontrol", "economic times", "goodreturns",
    "financial express", "world gold council", "reuters", "bloomberg",
    "business standard", "livemint", "bankbazaar", "goldprice", "kitco"
]


class CommodityValidator(BaseLiveValidator):
    """Domain validator for Gold, Silver, and commodity market data."""

    def validate(self, payload: dict, source: str) -> Tuple[bool, float, str]:
        if not payload:
            return False, 0.0, "Empty payload"

        asset = str(payload.get("asset", "")).lower()
        price = payload.get("price_numeric")
        unit = str(payload.get("unit", "")).lower()
        currency = str(payload.get("currency", "")).upper()

        if not asset or price is None:
            return False, 0.0, "Missing required fields (asset, price_numeric)"

        try:
            price_val = float(price)
        except (ValueError, TypeError):
            return False, 0.0, f"Invalid numeric price format: {price}"

        if price_val <= 0:
            return False, 0.0, f"Non-positive commodity price: {price_val}"

        # 1. Source Trust Check
        source_lower = source.lower()
        is_trusted_source = any(ts in source_lower for ts in TRUSTED_COMMODITY_SOURCES)
        if not is_trusted_source:
            logger.warning("[COMMODITY-VALIDATOR] Source '%s' not in trusted whitelist", source)

        # 2. Sanity bounds & Unit Validation
        if "gold" in asset:
            # Gold unit bounds in INR (₹)
            if currency == "INR":
                if "gram" in unit and "10" not in unit:
                    # Gold per gram: reasonable bounds ~₹4,000 to ₹15,000 per gram
                    if not (4000 <= price_val <= 15000):
                        return False, 0.0, f"Gold price per gram out of realistic bounds: ₹{price_val}"
                elif "10" in unit or "tola" in unit:
                    # Gold per 10 grams: ~₹40,000 to ₹150,000
                    if not (40000 <= price_val <= 150000):
                        return False, 0.0, f"Gold price per 10g out of realistic bounds: ₹{price_val}"
                elif "kg" in unit or "kilogram" in unit:
                    # Gold per kg: ~₹4,000,000 to ₹15,000,000
                    if not (4000000 <= price_val <= 15000000):
                        return False, 0.0, f"Gold price per kg out of realistic bounds: ₹{price_val}"
                elif "oz" in unit or "ounce" in unit:
                    # Gold per oz in INR: ~₹120,000 to ₹400,000
                    if not (120000 <= price_val <= 400000):
                        return False, 0.0, f"Gold price per oz in INR out of bounds: ₹{price_val}"

            # Gold unit bounds in USD ($)
            elif currency == "USD":
                if "oz" in unit or "ounce" in unit:
                    # Gold per oz: $1,500 to $4,000
                    if not (1500 <= price_val <= 4000):
                        return False, 0.0, f"Gold price per oz in USD out of bounds: ${price_val}"
                elif "gram" in unit:
                    # Gold per gram: $50 to $130
                    if not (50 <= price_val <= 130):
                        return False, 0.0, f"Gold price per gram in USD out of bounds: ${price_val}"

        elif "silver" in asset:
            # Silver unit bounds in INR (₹)
            if currency == "INR":
                if "gram" in unit and "10" not in unit and "kg" not in unit:
                    # Silver per gram: ~₹50 to ₹250 per gram
                    if not (50 <= price_val <= 250):
                        return False, 0.0, f"Silver price per gram out of bounds: ₹{price_val}"
                elif "kg" in unit or "kilogram" in unit:
                    # Silver per kg: ~₹50,000 to ₹250,000
                    if not (50000 <= price_val <= 250000):
                        return False, 0.0, f"Silver price per kg out of bounds: ₹{price_val}"
                elif "10" in unit:
                    # Silver per 10g: ~₹500 to ₹2,500
                    if not (500 <= price_val <= 2500):
                        return False, 0.0, f"Silver price per 10g out of bounds: ₹{price_val}"

            elif currency == "USD":
                if "oz" in unit or "ounce" in unit:
                    # Silver per oz: $15 to $60
                    if not (15 <= price_val <= 60):
                        return False, 0.0, f"Silver price per oz in USD out of bounds: ${price_val}"

        # 3. Unit Conversion Sanity Check if secondary conversions are provided in payload
        if "converted_per_gram" in payload:
            per_gram = float(payload["converted_per_gram"])
            if "kg" in unit:
                expected = price_val / 1000.0
                if abs(per_gram - expected) / expected > 0.05:  # >5% math error
                    return False, 0.0, f"Invalid unit conversion ratio: {price_val}/kg vs {per_gram}/g"
            elif "10" in unit:
                expected = price_val / 10.0
                if abs(per_gram - expected) / expected > 0.05:
                    return False, 0.0, f"Invalid unit conversion ratio: {price_val}/10g vs {per_gram}/g"

        confidence = 0.95 if is_trusted_source else 0.85
        return True, confidence, f"Validated commodity payload ({asset.title()} {currency} {price_val} {unit})"

"""
Jarvis AIOS — Live Commodity Tool
---------------------------------

Fetches live commodity data (Gold, Silver, Platinum, Spot Metals), parses structured payload,
validates through CommodityValidator, and returns a verified ToolResult contract.
"""

import re
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from app.Tools.live_information.contracts import ToolResult
from app.Tools.live_information.validators.commodity_validator import CommodityValidator
from app.Tools.search_providers.factory import SearchProviderFactory

logger = logging.getLogger(__name__)


class CommodityTool:
    """Tool for fetching and validating live commodity prices."""

    def __init__(self) -> None:
        self.validator = CommodityValidator()

    def execute(self, query: str) -> ToolResult:
        logger.info("[COMMODITY-TOOL] Executing live search for query='%s'", query)
        q_lower = query.lower()

        # Query Expansion for optimal live price retrieval
        expanded_query = query
        if "gold" in q_lower:
            expanded_query = f"live gold rate per gram 24k 22k India today {query}"
        elif "silver" in q_lower:
            expanded_query = f"live silver price per gram kg India today {query}"

        provider = SearchProviderFactory.get_provider(query=expanded_query)
        search_res = provider.search(query=expanded_query, num_results=5)

        if search_res.status != "success" or not search_res.results:
            logger.error("[COMMODITY-TOOL] Search failed or returned 0 results: status=%s", search_res.status)
            return ToolResult(
                success=False,
                verified=False,
                confidence=0.0,
                source=provider.name,
                error=search_res.error or "Search returned no parseable commodity data",
            )

        # Parse structured payload from top search snippets
        payload, source_used = self._parse_snippets(query, search_res.results)

        if not payload:
            logger.warning("[COMMODITY-TOOL] Could not extract structured commodity metrics from snippets")
            return ToolResult(
                success=False,
                verified=False,
                confidence=0.0,
                source=provider.name,
                error="Could not parse verified numeric price and units from search response",
            )

        # Run domain validation
        is_valid, confidence, reason = self.validator.validate(payload, source_used)
        logger.info("[COMMODITY-TOOL] Validation result: is_valid=%s confidence=%.2f reason='%s'", is_valid, confidence, reason)

        if not is_valid or confidence < 0.8:
            return ToolResult(
                success=True,
                verified=False,
                confidence=confidence,
                source=source_used,
                payload=payload,
                error=f"Commodity validation failed: {reason}",
            )

        return ToolResult(
            success=True,
            verified=True,
            confidence=confidence,
            source=source_used,
            timestamp=datetime.now(timezone.utc),
            payload=payload,
        )

    def _parse_snippets(self, original_query: str, results: list) -> tuple[Dict[str, Any], str]:
        q_lower = original_query.lower()

        for r in results:
            text = f"{r.title} {r.snippet}"
            source = r.source or r.url or "Web Search"

            # 1. Regex for Indian Gold Rate per gram / 10g (e.g. "24K Gold is ₹7,450 per gram" or "₹74,500 per 10 grams")
            if "gold" in q_lower:
                # Per 10g match: e.g. ₹74,500 / 10g or Rs 74500 per 10 gram
                m_10g = re.search(r'(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(?:per|\/)?\s*10\s*(?:grams?|g|tola)', text, re.IGNORECASE)
                if m_10g:
                    p10_str = m_10g.group(1).replace(",", "")
                    try:
                        p10_val = float(p10_str)
                        p1_val = round(p10_val / 10.0, 2)
                        purity = "24K" if "24" in text else ("22K" if "22" in text else "Standard")
                        return {
                            "asset": "Gold",
                            "purity": purity,
                            "price_numeric": p1_val,
                            "unit": "per gram",
                            "currency": "INR",
                            "price_10g": p10_val,
                            "converted_per_gram": p1_val,
                            "formatted_string": f"₹{p1_val:,} per gram (₹{p10_val:,} per 10 grams)",
                        }, source
                    except ValueError:
                        pass

                # Per 1g match: e.g. ₹7,450 per gram
                m_1g = re.search(r'(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(?:per|\/)?\s*(?:1\s*)?(?:gram|g)\b', text, re.IGNORECASE)
                if m_1g:
                    p1_str = m_1g.group(1).replace(",", "")
                    try:
                        p1_val = float(p1_str)
                        purity = "24K" if "24" in text else ("22K" if "22" in text else "Standard")
                        return {
                            "asset": "Gold",
                            "purity": purity,
                            "price_numeric": p1_val,
                            "unit": "per gram",
                            "currency": "INR",
                            "price_10g": round(p1_val * 10, 2),
                            "converted_per_gram": p1_val,
                            "formatted_string": f"₹{p1_val:,} per gram",
                        }, source
                    except ValueError:
                        pass

            # 2. Regex for Silver Rate per gram / per kg (e.g. "Silver rate is ₹88 per gram" or "₹88,000 per kg")
            if "silver" in q_lower:
                m_kg = re.search(r'(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(?:per|\/)?\s*(?:1\s*)?(?:kg|kilogram)', text, re.IGNORECASE)
                if m_kg:
                    pkg_str = m_kg.group(1).replace(",", "")
                    try:
                        pkg_val = float(pkg_str)
                        p1_val = round(pkg_val / 1000.0, 2)
                        return {
                            "asset": "Silver",
                            "price_numeric": p1_val,
                            "unit": "per gram",
                            "currency": "INR",
                            "price_per_kg": pkg_val,
                            "converted_per_gram": p1_val,
                            "formatted_string": f"₹{p1_val:,} per gram (₹{pkg_val:,} per kg)",
                        }, source
                    except ValueError:
                        pass

                m_gram = re.search(r'(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(?:per|\/)?\s*(?:1\s*)?(?:gram|g)\b', text, re.IGNORECASE)
                if m_gram:
                    p1_str = m_gram.group(1).replace(",", "")
                    try:
                        p1_val = float(p1_str)
                        return {
                            "asset": "Silver",
                            "price_numeric": p1_val,
                            "unit": "per gram",
                            "currency": "INR",
                            "price_per_kg": round(p1_val * 1000, 2),
                            "converted_per_gram": p1_val,
                            "formatted_string": f"₹{p1_val:,} per gram",
                        }, source
                    except ValueError:
                        pass

        return {}, ""

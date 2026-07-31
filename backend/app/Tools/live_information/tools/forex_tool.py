"""
Jarvis AIOS — Live Forex Tool
-----------------------------

Fetches live foreign exchange rates (USD-INR, EUR-USD, etc.),
validates through ForexValidator, and returns ToolResult.
"""

import re
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from app.Tools.live_information.contracts import ToolResult
from app.Tools.live_information.validators.forex_validator import ForexValidator
from app.Tools.search_providers.factory import SearchProviderFactory

logger = logging.getLogger(__name__)


class ForexTool:
    """Tool for fetching and validating foreign exchange rates."""

    def __init__(self) -> None:
        self.validator = ForexValidator()

    def execute(self, query: str) -> ToolResult:
        logger.info("[FOREX-TOOL] Executing live search for query='%s'", query)
        expanded_query = f"live exchange rate RBI XE Moneycontrol today {query}"
        provider = SearchProviderFactory.get_provider(query=expanded_query)
        search_res = provider.search(query=expanded_query, num_results=5)

        if search_res.status != "success" or not search_res.results:
            return ToolResult(
                success=False,
                verified=False,
                confidence=0.0,
                source=provider.name,
                error=search_res.error or "Search returned no forex exchange rate data",
            )

        payload, source_used = self._parse_snippets(query, search_res.results)

        if not payload:
            return ToolResult(
                success=False,
                verified=False,
                confidence=0.0,
                source=provider.name,
                error="Could not parse verified exchange rate from search response",
            )

        is_valid, confidence, reason = self.validator.validate(payload, source_used)
        if not is_valid or confidence < 0.8:
            return ToolResult(
                success=True,
                verified=False,
                confidence=confidence,
                source=source_used,
                payload=payload,
                error=f"Forex validation failed: {reason}",
            )

        return ToolResult(
            success=True,
            verified=True,
            confidence=confidence,
            source=source_used,
            timestamp=datetime.now(timezone.utc),
            payload=payload,
        )

    def _parse_snippets(self, query: str, results: list) -> tuple[Dict[str, Any], str]:
        for r in results:
            text = f"{r.title} {r.snippet}"
            source = r.source or r.url or "RBI/XE"
            # Regex for Forex Rate e.g. "1 USD = 83.50 INR" or "USD to INR exchange rate is 83.50"
            m = re.search(r'1\s*([A-Z]{3})\s*=\s*([\d,]+(?:\.\d+)?)\s*([A-Z]{3})', text, re.IGNORECASE)
            if m:
                base = m.group(1).upper()
                rate_str = m.group(2).replace(",", "")
                target = m.group(3).upper()
                try:
                    rate_val = float(rate_str)
                    return {
                        "base_currency": base,
                        "target_currency": target,
                        "rate": rate_val,
                        "formatted_string": f"1 {base} = {rate_val} {target}",
                    }, source
                except ValueError:
                    pass

        return {}, ""

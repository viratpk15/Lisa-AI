"""
Jarvis AIOS — Live Stock Market Tool
------------------------------------

Fetches live stock market prices, indices (NSE/BSE), parses structured payload,
validates through StockValidator, and returns ToolResult.
"""

import re
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from app.Tools.live_information.contracts import ToolResult
from app.Tools.live_information.validators.stock_validator import StockValidator
from app.Tools.search_providers.factory import SearchProviderFactory

logger = logging.getLogger(__name__)


class StockTool:
    """Tool for fetching and validating stock market prices & indices."""

    def __init__(self) -> None:
        self.validator = StockValidator()

    def execute(self, query: str) -> ToolResult:
        logger.info("[STOCK-TOOL] Executing live search for query='%s'", query)
        expanded_query = f"live stock price NSE BSE Moneycontrol today {query}"
        provider = SearchProviderFactory.get_provider(query=expanded_query)
        search_res = provider.search(query=expanded_query, num_results=5)

        if search_res.status != "success" or not search_res.results:
            return ToolResult(
                success=False,
                verified=False,
                confidence=0.0,
                source=provider.name,
                error=search_res.error or "Search returned no stock market data",
            )

        payload, source_used = self._parse_snippets(query, search_res.results)

        if not payload:
            return ToolResult(
                success=False,
                verified=False,
                confidence=0.0,
                source=provider.name,
                error="Could not parse verified stock price from search response",
            )

        is_valid, confidence, reason = self.validator.validate(payload, source_used)
        if not is_valid or confidence < 0.8:
            return ToolResult(
                success=True,
                verified=False,
                confidence=confidence,
                source=source_used,
                payload=payload,
                error=f"Stock validation failed: {reason}",
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
            source = r.source or r.url or "NSE/BSE"
            # Regex for Stock / Index Price e.g. "Nifty 50 is trading at 24,500.50 (+0.4%)" or "Reliance Industries ₹3,120.00"
            m = re.search(r'([\w\s]+?)\s*(?:is trading at|price|at|:)?\s*(?:₹|rs\.?|inr|\$)\s*([\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
            if m:
                symbol = m.group(1).strip()
                p_str = m.group(2).replace(",", "")
                try:
                    price_val = float(p_str)
                    currency = "INR" if "₹" in text or "rs" in text.lower() or "inr" in text.lower() else "USD"
                    return {
                        "symbol": symbol[:30],
                        "asset": symbol[:30],
                        "price_numeric": price_val,
                        "currency": currency,
                        "formatted_string": f"{symbol[:30]}: {currency} {price_val:,}",
                    }, source
                except ValueError:
                    pass

        return {}, ""

"""
Jarvis AIOS — Search Intent Classifier
---------------------------------------

Lightweight, deterministic intent classifier for search queries.
Uses scored signal matching to select the optimal search provider
(Serper for factual queries, Tavily for research/agentic queries).

No external dependencies. No ML model. Fully explainable via logs.

Usage:
    from app.Tools.search_providers.classifier import SearchIntentClassifier

    result = SearchIntentClassifier.classify("Compare LangGraph vs CrewAI")
    # result.provider     -> "tavily"
    # result.intent       -> "research"
    # result.confidence   -> 0.9
    # result.reasoning    -> "research_score=6 > factual_score=0 (+2 margin)"
    # result.search_depth -> "advanced"
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Signal tables
# ---------------------------------------------------------------------------

# Research signals — multi-source synthesis, comparison, investigation, trends.
_RESEARCH_SIGNALS: dict[str, int] = {
    " vs ": 4, " versus ": 4, "compare ": 4, "comparison": 3,
    "which is better": 4, "pros and cons": 3, "tradeoffs": 3, "trade-offs": 3,
    "research ": 4, "investigate": 4, "deep dive": 4, "in depth": 3,
    "analyze ": 4, "analyse ": 4, "analysis of": 3, "internals of": 3,
    "how does": 2, "architecture of": 3, "under the hood": 3,
    "future of": 3, "trends in": 3, "evolution of": 3, "roadmap": 2,
    "explain the": 2, "overview of": 2, "landscape": 2,
    "best ": 2, "top 5": 2, "top 10": 2, "recommend": 2,
    "should i use": 4, "which should": 4, "what should": 2,
    "summarize these": 4, "summarize the following": 4,
    "based on these": 4, "from these articles": 4, "across sources": 4,
    "agentic ai": 3, "autonomous agents": 3, "llm research": 3,
    "mcp architecture": 3, "rag framework": 3,
}

# Factual signals — specific, current, single-source answers.
_FACTUAL_SIGNALS: dict[str, int] = {
    "latest ": 3, "newest ": 3, "current ": 2, "right now": 4,
    "today": 3, "today's": 3, "this week": 3, "this year": 2,
    "breaking": 4, "just released": 4,
    "news": 2, "headlines": 3, "earnings": 4,
    "stock ": 3, "stock price": 4, "price of": 3, "cost of": 3,
    "version": 4, "release notes": 4, "changelog": 4, "pip install": 4, "pypi": 4,
    "weather": 4, "rain": 3, "temperature": 3, "forecast": 4, "humidity": 3,
    "documentation": 3, "docs for": 3, "github ": 3, "repository": 3, "readme": 3,
    "who is ": 3, "when was ": 3, "how much does": 3, "how many": 2,
    "what is the latest": 4, "what are the latest": 4,
    "what is the current": 4, "what is the new": 3,
}

# Live information domain signals — trigger mandatory tool execution & fail-closed gate
_LIVE_DOMAINS: dict[str, list[str]] = {
    "commodity": [
        "gold", "silver", "platinum", "palladium", "commodity", "commodities", "bullion",
        "gold rate", "silver rate", "gold price", "silver price", "per gram", "per 10g", "per kg", "per oz", "tola"
    ],
    "stocks": [
        "stock", "stocks", "share", "shares", "nifty", "sensex", "mcx", "nse", "bse",
        "stock price", "top gainers", "top losers", "market index"
    ],
    "crypto": [
        "crypto", "cryptocurrency", "bitcoin", "btc", "ethereum", "eth", "solana", "sol"
    ],
    "weather": [
        "weather", "temperature", "forecast", "rain", "humidity"
    ],
    "forex": [
        "currency", "exchange rate", "forex", "usd to inr", "eur to inr", "usd-inr", "gbp"
    ]
}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ClassifierResult:
    """Result produced by SearchIntentClassifier.classify()."""
    provider: str        # "serper" | "tavily"
    intent: str          # "factual" | "research" | "unknown"
    confidence: float    # 0.0 – 1.0
    reasoning: str       # Human-readable log string
    search_depth: str    # "basic" | "advanced"
    is_live_info: bool = False
    domain: str = ""     # "commodity" | "stocks" | "crypto" | "weather" | "forex"


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class SearchIntentClassifier:
    """
    Lightweight, deterministic search intent classifier.

    Scores each query against two weighted signal tables and selects
    the optimal search provider. Ties and low-confidence cases always
    default to Serper (faster, cheaper). Never executes both providers.
    """

    _RESEARCH_MARGIN: int = 2  # research must beat factual by this much to win

    @classmethod
    def classify(cls, query: str) -> ClassifierResult:
        q = query.lower()

        # Check for live information domains
        detected_domain = ""
        is_live = False
        for domain, keywords in _LIVE_DOMAINS.items():
            if any(kw in q for kw in keywords):
                is_live = True
                detected_domain = domain
                break

        research_score = sum(w for kw, w in _RESEARCH_SIGNALS.items() if kw in q)
        factual_score  = sum(w for kw, w in _FACTUAL_SIGNALS.items()  if kw in q)
        if is_live:
            factual_score += 5  # Boost factual score for live data queries

        total = research_score + factual_score

        if research_score > factual_score + cls._RESEARCH_MARGIN:
            intent        = "research"
            provider      = "tavily"
            search_depth  = "advanced"
            confidence    = cls._confidence(research_score, factual_score, total)
            reasoning     = (
                f"research_score={research_score} > factual_score={factual_score} "
                f"(+{cls._RESEARCH_MARGIN} margin) → Tavily (search_depth=advanced)"
            )
        else:
            intent        = "factual" if (total > 0 or is_live) else "unknown"
            provider      = "serper"
            search_depth  = "basic"
            confidence    = cls._confidence(factual_score, research_score, total)
            reasoning     = (
                f"factual_score={factual_score}, research_score={research_score} "
                f"(is_live_info={is_live}, domain={detected_domain})"
            )

        result = ClassifierResult(
            provider=provider,
            intent=intent,
            confidence=confidence,
            reasoning=reasoning,
            search_depth=search_depth,
            is_live_info=is_live,
            domain=detected_domain,
        )

        logger.info(
            "[SEARCH-CLASSIFIER] query='%s' provider=%s intent=%s is_live_info=%s domain=%s "
            "confidence=%.2f reasoning='%s'",
            query[:60], result.provider, result.intent, result.is_live_info, result.domain,
            result.confidence, result.reasoning,
        )

        return result

    @staticmethod
    def _confidence(winner_score: int, loser_score: int, total: int) -> float:
        if total == 0:
            return 0.5
        return min(1.0, 0.5 + (winner_score - loser_score) / (2 * max(total, 1)))


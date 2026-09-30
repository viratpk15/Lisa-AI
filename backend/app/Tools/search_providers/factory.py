"""
Jarvis AIOS — Search Provider Factory
-------------------------------------

Factory for instantiating search providers dynamically based on the query
intent (via SearchIntentClassifier) and environment configuration.

Priority chains:
  Factual  → Serper → Tavily → Brave → Fallback
  Research → Tavily → Serper → Fallback
"""

import logging
from typing import Optional

from app.Config import settings
from app.Tools.search_providers.base import SearchProvider
from app.Tools.search_providers.classifier import SearchIntentClassifier
from app.Tools.search_providers.tavily import TavilyProvider
from app.Tools.search_providers.brave import BraveProvider
from app.Tools.search_providers.serper import SerperProvider
from app.Tools.search_providers.fallback import FallbackProvider

logger = logging.getLogger(__name__)


class SearchProviderFactory:
    """
    Factory that instantiates the appropriate SearchProvider for each query.

    Provider selection priority:
        Factual queries  → Serper  → Tavily → Brave → Fallback
        Research queries → Tavily  → Serper → Fallback

    An explicit SEARCH_PROVIDER env var overrides classifier routing.
    """

    @staticmethod
    def get_providers_chain(
        query: Optional[str] = None,
        query_type: Optional[str] = None,
        search_depth: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> list[SearchProvider]:
        """
        Build the ordered fallback chain of available SearchProviders.

        Priority chains:
          Factual  → Serper → Tavily → Brave → Fallback
          Research → Tavily → Serper → Brave → Fallback
        """
        # ── Resolve keys from settings ──────────────────────────────────────
        if api_key is not None:
            tavily_key = api_key
            serper_key = api_key
            brave_key  = api_key
        else:
            tavily_key = settings.TAVILY_API_KEY
            serper_key = settings.SERPER_API_KEY
            brave_key  = settings.BRAVE_API_KEY

        # ── Explicit SEARCH_PROVIDER env var overrides everything ────────────
        provider_override = settings.SEARCH_PROVIDER.lower()
        if provider_override not in ("auto", ""):
            overridden = SearchProviderFactory._build(
                provider_override, tavily_key, serper_key, brave_key, search_depth
            )
            return [overridden, FallbackProvider()]

        # ── Run intent classifier when provider is "auto" ────────────────────
        if query_type is None and query:
            classification = SearchIntentClassifier.classify(query)
            query_type   = classification.intent
            search_depth = search_depth or classification.search_depth

        chain: list[SearchProvider] = []
        # ── Research chain: Tavily → Serper → Brave → Fallback ───────────────
        if query_type == "research":
            if tavily_key:
                chain.append(TavilyProvider(api_key=tavily_key, search_depth=search_depth or "advanced"))
            if serper_key:
                chain.append(SerperProvider(api_key=serper_key))
            if brave_key:
                chain.append(BraveProvider(api_key=brave_key))
        else:
            # ── Factual chain: Serper → Tavily → Brave → Fallback ───────────
            if serper_key:
                chain.append(SerperProvider(api_key=serper_key))
            if tavily_key:
                chain.append(TavilyProvider(api_key=tavily_key, search_depth="basic"))
            if brave_key:
                chain.append(BraveProvider(api_key=brave_key))

        chain.append(FallbackProvider())
        return chain

    @staticmethod
    def get_provider(
        query: Optional[str] = None,
        query_type: Optional[str] = None,   # explicit override ("factual"|"research")
        search_depth: Optional[str] = None, # explicit override ("basic"|"advanced")
        api_key: Optional[str] = None,
    ) -> SearchProvider:
        """Select and return the primary SearchProvider from the failover chain."""
        chain = SearchProviderFactory.get_providers_chain(
            query=query, query_type=query_type, search_depth=search_depth, api_key=api_key
        )
        return chain[0] if chain else FallbackProvider()

    @staticmethod
    def _build(
        name: str,
        tavily_key: Optional[str],
        serper_key: Optional[str],
        brave_key: Optional[str],
        search_depth: Optional[str],
    ) -> SearchProvider:
        """Instantiate a provider by explicit name."""
        if name == "tavily" and tavily_key:
            logger.info("[SEARCH-FACTORY] Explicit override → TavilyProvider")
            return TavilyProvider(api_key=tavily_key, search_depth=search_depth or "basic")
        if name == "serper" and serper_key:
            logger.info("[SEARCH-FACTORY] Explicit override → SerperProvider")
            return SerperProvider(api_key=serper_key)
        if name == "brave" and brave_key:
            logger.info("[SEARCH-FACTORY] Explicit override → BraveProvider")
            return BraveProvider(api_key=brave_key)
        logger.info("[SEARCH-FACTORY] Explicit override '%s' failed (no key) → FallbackProvider", name)
        return FallbackProvider()

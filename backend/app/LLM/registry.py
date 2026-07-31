"""
Jarvis AIOS — LLM Provider Registry
------------------------------------

Registers, discovers, and resolves provider classes by provider_name string.
Extensible without modifying the core runtime or router logic.
"""

import logging
from typing import Dict, Type
from app.LLM.base import BaseLLMProvider
from app.LLM.providers.groq_provider import GroqProvider
from app.LLM.providers.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry maintaining available provider driver classes."""

    def __init__(self):
        self._registry: Dict[str, Type[BaseLLMProvider]] = {}
        # Register default initial drivers
        self.register("groq", GroqProvider)
        self.register("ollama", OllamaProvider)

    def register(self, provider_name: str, provider_cls: Type[BaseLLMProvider]) -> None:
        name = provider_name.lower().strip()
        self._registry[name] = provider_cls
        logger.info("[LLM-REGISTRY] Registered provider driver '%s'", name)

    def get(self, provider_name: str) -> Type[BaseLLMProvider]:
        name = provider_name.lower().strip()
        if name not in self._registry:
            # Fallback to Ollama or Groq if unknown provider name
            if "ollama" in self._registry:
                return self._registry["ollama"]
            return self._registry["groq"]
        return self._registry[name]

    def list_providers(self) -> list[str]:
        return list(self._registry.keys())


provider_registry = ProviderRegistry()

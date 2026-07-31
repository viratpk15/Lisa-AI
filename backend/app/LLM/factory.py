"""
Jarvis AIOS — LLM Provider Factory
----------------------------------

Stateless factory resolving and instantiating BaseLLMProvider instances from
ProviderConfig objects on-demand.
"""

import logging
from app.LLM.base import BaseLLMProvider, ProviderConfig
from app.LLM.registry import provider_registry

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Stateless factory instantiating LLM drivers from configuration."""

    @staticmethod
    def create_provider(config: ProviderConfig) -> BaseLLMProvider:
        provider_cls = provider_registry.get(config.provider_name)
        return provider_cls(config)


provider_factory = ProviderFactory()

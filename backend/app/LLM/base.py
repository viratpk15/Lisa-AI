"""
Jarvis AIOS — Base Provider Interface, Capabilities & Configuration
------------------------------------------------------------------

Defines standardized ProviderConfig, ProviderCapabilities, custom exceptions,
and BaseLLMProvider abstract base class for LLM drivers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional
from langchain_core.messages import BaseMessage, AIMessage


class RecoverableLLMError(Exception):
    """Exception raised for recoverable infrastructure errors (429, 5xx, timeout, connect error, missing API key)."""
    pass


class UnrecoverableLLMError(Exception):
    """Exception raised for unrecoverable errors (invalid prompt, validation error, schema bug)."""
    pass


@dataclass
class ProviderCapabilities:
    supports_streaming: bool = True
    supports_tools: bool = True
    supports_embeddings: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    supports_json_mode: bool = True
    supports_reasoning: bool = False


@dataclass
class ProviderConfig:
    provider_name: str
    model_id: str
    display_name: str = ""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout_seconds: float = 30.0
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {"max_retries": 2})
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseLLMProvider(ABC):
    """Abstract Base Class for all LLM providers in Jarvis AIOS."""

    def __init__(self, config: ProviderConfig):
        self.config = config

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        pass

    @abstractmethod
    def chat(self, messages: List[BaseMessage], **kwargs: Any) -> AIMessage:
        """Synchronously execute chat completion and return AIMessage."""
        pass

    @abstractmethod
    def stream(self, messages: List[BaseMessage], **kwargs: Any) -> Generator[str, None, None]:
        """Stream token strings in a provider-agnostic manner."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return provider health status, latency, and operational details."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """Return available model identifiers supported by provider."""
        pass

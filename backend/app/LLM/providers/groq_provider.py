"""
Jarvis AIOS — Groq Cloud LLM Provider Driver
---------------------------------------------

Wraps ChatGroq with capability discovery, health checks, and standardized
error translation for recoverable rate limits (429), timeouts, and network failures.
"""

import logging
import os
import time
from typing import Any, Dict, Generator, List
from langchain_core.messages import BaseMessage, AIMessage
from langchain_groq import ChatGroq

from app.LLM.base import (
    BaseLLMProvider,
    ProviderCapabilities,
    ProviderConfig,
    RecoverableLLMError,
    UnrecoverableLLMError,
)

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq Cloud Provider Driver."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        api_key = config.api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("[GROQ-DRIVER] GROQ_API_KEY is missing or empty.")

        self._llm = ChatGroq(
            model=config.model_id or "llama-3.3-70b-versatile",
            api_key=api_key,
            request_timeout=config.timeout_seconds,
        )

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_streaming=True,
            supports_tools=True,
            supports_embeddings=False,
            supports_vision=False,
            supports_audio=False,
            supports_json_mode=True,
            supports_reasoning=False,
        )

    def chat(self, messages: List[BaseMessage], **kwargs: Any) -> AIMessage:
        if not self.config.api_key and not os.getenv("GROQ_API_KEY"):
            raise RecoverableLLMError("Groq API Key missing or unconfigured.")

        try:
            return self._llm.invoke(messages, **kwargs)
        except Exception as exc:
            err_msg = str(exc).lower()
            if any(k in err_msg for k in ["429", "rate limit", "quota", "timeout", "connection", "connect", "500", "503", "unavailable"]):
                raise RecoverableLLMError(f"Groq Recoverable Infrastructure Error: {exc}") from exc
            raise UnrecoverableLLMError(f"Groq Execution Error: {exc}") from exc

    def stream(self, messages: List[BaseMessage], **kwargs: Any) -> Generator[str, None, None]:
        if not self.config.api_key and not os.getenv("GROQ_API_KEY"):
            raise RecoverableLLMError("Groq API Key missing or unconfigured.")

        try:
            for chunk in self._llm.stream(messages, **kwargs):
                token = getattr(chunk, "content", None)
                if token is None:
                    token = str(chunk)
                if token:
                    yield str(token)
        except Exception as exc:
            err_msg = str(exc).lower()
            if any(k in err_msg for k in ["429", "rate limit", "quota", "timeout", "connection", "connect", "500", "503", "unavailable"]):
                raise RecoverableLLMError(f"Groq Streaming Recoverable Error: {exc}") from exc
            raise UnrecoverableLLMError(f"Groq Streaming Unrecoverable Error: {exc}") from exc

    def health_check(self) -> Dict[str, Any]:
        start = time.time()
        has_key = bool(self.config.api_key or os.getenv("GROQ_API_KEY"))
        return {
            "provider": "groq",
            "model": self.config.model_id,
            "is_healthy": has_key,
            "has_api_key": has_key,
            "latency_ms": round((time.time() - start) * 1000, 2),
        }

    def list_models(self) -> List[str]:
        return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]

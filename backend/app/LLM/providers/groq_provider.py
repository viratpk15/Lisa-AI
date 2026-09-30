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
from pydantic import SecretStr
from langchain_core.messages import BaseMessage, AIMessage
from langchain_groq import ChatGroq

from app.LLM.base import (
    BaseLLMProvider,
    ProviderCapabilities,
    ProviderConfig,
    RecoverableLLMError,
)

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq Cloud Provider Driver."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.getenv("GROQ_API_KEY")
        self.model_id = config.model_id or "llama-3.3-70b-versatile"
        self._llm = None

        if not self.api_key:
            logger.warning("[GROQ-DRIVER] GROQ_API_KEY is missing or empty.")
        else:
            try:
                self._llm = ChatGroq(
                    model=self.model_id,
                    api_key=SecretStr(self.api_key),
                )
            except Exception as exc:
                logger.warning("[GROQ-DRIVER] Initialization error: %s", exc)
                self._llm = None

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
        if not self._llm or not self.api_key:
            raise RecoverableLLMError("Groq API Key missing or unconfigured.")

        try:
            return self._llm.invoke(messages, **kwargs)
        except Exception as exc:
            err_msg = str(exc).lower()
            if any(k in err_msg for k in ["429", "rate limit", "quota", "timeout", "connection", "connect", "500", "503", "unavailable", "404", "model_not_found", "does not exist", "not found"]):
                raise RecoverableLLMError(f"Groq Recoverable Infrastructure Error: {exc}") from exc
            raise RecoverableLLMError(f"Groq Execution Error: {exc}") from exc

    def stream(self, messages: List[BaseMessage], **kwargs: Any) -> Generator[str, None, None]:
        if not self._llm or not self.api_key:
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
            if any(k in err_msg for k in ["429", "rate limit", "quota", "timeout", "connection", "connect", "500", "503", "unavailable", "404", "model_not_found", "does not exist", "not found"]):
                raise RecoverableLLMError(f"Groq Streaming Recoverable Error: {exc}") from exc
            raise RecoverableLLMError(f"Groq Streaming Error: {exc}") from exc

    def health_check(self) -> Dict[str, Any]:
        start = time.time()
        has_key = bool(self.api_key)
        return {
            "provider": "groq",
            "model": self.model_id,
            "is_healthy": has_key and self._llm is not None,
            "has_api_key": has_key,
            "latency_ms": round((time.time() - start) * 1000, 2),
        }

    def list_models(self) -> List[str]:
        return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]

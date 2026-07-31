"""
Jarvis AIOS — Ollama Local LLM Provider Driver
-----------------------------------------------

Wraps ChatOllama or HTTP REST for local offline inference with capability discovery
and connection health checks.
"""

import json
import logging
import os
import time
import urllib.request
from typing import Any, Dict, Generator, List
from langchain_core.messages import BaseMessage, AIMessage

from app.LLM.base import (
    BaseLLMProvider,
    ProviderCapabilities,
    ProviderConfig,
    RecoverableLLMError,
    UnrecoverableLLMError,
)

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Ollama Local Provider Driver."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = config.model_id or "llama3:latest"

        # Try importing ChatOllama or fallback to HTTP REST
        self._chat_ollama = None
        try:
            from langchain_community.chat_models import ChatOllama
            self._chat_ollama = ChatOllama(model=self.model_name, base_url=self.base_url)
        except Exception:
            pass

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_streaming=True,
            supports_tools=True,
            supports_embeddings=False,
            supports_vision=True,
            supports_audio=False,
            supports_json_mode=True,
            supports_reasoning=False,
        )

    def chat(self, messages: List[BaseMessage], **kwargs: Any) -> AIMessage:
        if self._chat_ollama:
            try:
                return self._chat_ollama.invoke(messages, **kwargs)
            except Exception as exc:
                err_msg = str(exc).lower()
                if any(k in err_msg for k in ["connection", "refused", "timeout", "unavailable", "500", "503"]):
                    raise RecoverableLLMError(f"Ollama Connection Error: {exc}") from exc
                raise UnrecoverableLLMError(f"Ollama Invocation Error: {exc}") from exc

        # HTTP REST Fallback
        prompt_text = "\n".join([f"{m.__class__.__name__}: {m.content}" for m in messages])
        try:
            url = f"{self.base_url}/api/generate"
            payload = json.dumps({"model": self.model_name, "prompt": prompt_text, "stream": False}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return AIMessage(content=data.get("response", ""))
        except Exception as exc:
            raise RecoverableLLMError(f"Ollama REST Error: {exc}") from exc

    def stream(self, messages: List[BaseMessage], **kwargs: Any) -> Generator[str, None, None]:
        if self._chat_ollama:
            try:
                for chunk in self._chat_ollama.stream(messages, **kwargs):
                    token = getattr(chunk, "content", None)
                    if token is None:
                        token = str(chunk)
                    if token:
                        yield str(token)
                return
            except Exception as exc:
                err_msg = str(exc).lower()
                if any(k in err_msg for k in ["connection", "refused", "timeout", "unavailable", "500", "503"]):
                    raise RecoverableLLMError(f"Ollama Streaming Connection Error: {exc}") from exc
                raise UnrecoverableLLMError(f"Ollama Streaming Error: {exc}") from exc

        # HTTP REST Streaming Fallback
        prompt_text = "\n".join([f"{m.__class__.__name__}: {m.content}" for m in messages])
        try:
            url = f"{self.base_url}/api/generate"
            payload = json.dumps({"model": self.model_name, "prompt": prompt_text, "stream": True}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                for line in resp:
                    if line:
                        chunk_json = json.loads(line.decode("utf-8"))
                        txt = chunk_json.get("response", "")
                        if txt:
                            yield txt
        except Exception as exc:
            raise RecoverableLLMError(f"Ollama REST Streaming Error: {exc}") from exc

    def health_check(self) -> Dict[str, Any]:
        start = time.time()
        is_healthy = False
        try:
            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    is_healthy = True
        except Exception:
            is_healthy = False

        return {
            "provider": "ollama",
            "model": self.model_name,
            "base_url": self.base_url,
            "is_healthy": is_healthy,
            "latency_ms": round((time.time() - start) * 1000, 2),
        }

    def list_models(self) -> List[str]:
        return ["llama3:latest", "qwen2.5:3b", "qwen2.5"]

"""
Jarvis AIOS — NVIDIA NIM LLM Provider Driver
---------------------------------------------

Wraps NVIDIA NIM API (OpenAI-compatible) with capability discovery, health checks,
and standardized error translation for recoverable rate limits (429), timeouts, and network failures.
"""

import json
import logging
import os
import time
from typing import Any, Dict, Generator, List
import httpx
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage

from app.LLM.base import (
    BaseLLMProvider,
    ProviderCapabilities,
    ProviderConfig,
    RecoverableLLMError,
    UnrecoverableLLMError,
)

logger = logging.getLogger(__name__)


def _format_messages_for_api(messages: List[Any]) -> List[Dict[str, str]]:
    """Convert LangChain BaseMessages or strings to OpenAI/NVIDIA API format."""
    formatted = []
    for m in messages:
        if isinstance(m, str):
            formatted.append({"role": "user", "content": m})
            continue
        if isinstance(m, HumanMessage):
            role = "user"
        elif isinstance(m, AIMessage):
            role = "assistant"
        elif isinstance(m, SystemMessage):
            role = "system"
        else:
            role = getattr(m, "type", "user")
            if role == "human":
                role = "user"
            elif role == "ai":
                role = "assistant"
        content = getattr(m, "content", str(m))
        formatted.append({"role": role, "content": str(content)})
    return formatted


class NvidiaProvider(BaseLLMProvider):
    """NVIDIA NIM Provider Driver."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_NIM_API_KEY")
        self.base_url = (config.base_url or os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")).rstrip("/")
        self.model_id = config.model_id or "meta/llama-3.3-70b-instruct"
        if not self.api_key:
            logger.warning("[NVIDIA-NIM-DRIVER] NVIDIA_API_KEY is missing or empty.")

    @property
    def provider_name(self) -> str:
        return "nvidia"

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
        if not self.api_key:
            raise RecoverableLLMError("NVIDIA NIM API Key missing or unconfigured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_id,
            "messages": _format_messages_for_api(messages),
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                resp = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if resp.status_code in [429, 500, 502, 503, 504]:
                    raise RecoverableLLMError(f"NVIDIA NIM HTTP {resp.status_code}: {resp.text}")
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return AIMessage(content=content)
        except httpx.TimeoutException as exc:
            raise RecoverableLLMError(f"NVIDIA NIM Connection Timeout: {exc}") from exc
        except httpx.ConnectError as exc:
            raise RecoverableLLMError(f"NVIDIA NIM Connection Error: {exc}") from exc
        except RecoverableLLMError:
            raise
        except Exception as exc:
            err_msg = str(exc).lower()
            if any(k in err_msg for k in ["429", "rate limit", "quota", "timeout", "connection", "connect", "500", "503", "unavailable"]):
                raise RecoverableLLMError(f"NVIDIA NIM Recoverable Error: {exc}") from exc
            raise UnrecoverableLLMError(f"NVIDIA NIM Execution Error: {exc}") from exc

    def stream(self, messages: List[BaseMessage], **kwargs: Any) -> Generator[str, None, None]:
        if not self.api_key:
            raise RecoverableLLMError("NVIDIA NIM API Key missing or unconfigured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_id,
            "messages": _format_messages_for_api(messages),
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stream": True,
        }

        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload) as resp:
                    if resp.status_code in [429, 500, 502, 503, 504]:
                        raise RecoverableLLMError(f"NVIDIA NIM Streaming HTTP {resp.status_code}")
                    resp.raise_for_status()
                    for line in resp.iter_lines():
                        if not line:
                            continue
                        if line.startswith("data: "):
                            line_data = line[6:].strip()
                            if line_data == "[DONE]":
                                break
                            try:
                                chunk_json = json.loads(line_data)
                                choices = chunk_json.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    token = delta.get("content")
                                    if token:
                                        yield token
                            except json.JSONDecodeError:
                                continue
        except httpx.TimeoutException as exc:
            raise RecoverableLLMError(f"NVIDIA NIM Streaming Timeout: {exc}") from exc
        except httpx.ConnectError as exc:
            raise RecoverableLLMError(f"NVIDIA NIM Streaming Connect Error: {exc}") from exc
        except RecoverableLLMError:
            raise
        except Exception as exc:
            err_msg = str(exc).lower()
            if any(k in err_msg for k in ["429", "rate limit", "quota", "timeout", "connection", "connect", "500", "503", "unavailable"]):
                raise RecoverableLLMError(f"NVIDIA NIM Streaming Recoverable Error: {exc}") from exc
            raise UnrecoverableLLMError(f"NVIDIA NIM Streaming Unrecoverable Error: {exc}") from exc

    def health_check(self) -> Dict[str, Any]:
        start = time.time()
        has_key = bool(self.api_key)
        return {
            "provider": "nvidia",
            "model": self.model_id,
            "is_healthy": has_key,
            "has_api_key": has_key,
            "latency_ms": round((time.time() - start) * 1000, 2),
        }

    def list_models(self) -> List[str]:
        return ["meta/llama-3.3-70b-instruct", "meta/llama-3.1-8b-instruct", "mistralai/mistral-large-2407"]

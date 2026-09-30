"""
Jarvis AIOS — Production Stateless LLM Router & Failover Engine
----------------------------------------------------------------

Stateless router walking dynamic database-driven provider chains, executing pre-token
recoverable failovers (Groq -> Ollama), enforcing mid-stream token safety, and recording
observability metrics.
"""

import logging
import os
import time
from typing import Any, Dict, Generator, List
from langchain_core.messages import BaseMessage, AIMessage

from app.LLM.base import (
    ProviderConfig,
    RecoverableLLMError,
)
from app.LLM.factory import ProviderFactory
from app.Observability.manager import observability_manager

logger = logging.getLogger(__name__)


def is_production_env() -> bool:
    """Determine if running under production environment."""
    env = (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or "development").strip().lower()
    return env in ("production", "prod")


def format_provider_model(provider_name: str, model_id: str) -> str:
    """Format provider and model into a concise, readable badge string."""
    name_map = {
        "groq": "Groq",
        "nvidia": "NVIDIA",
        "mistral": "Mistral",
        "ollama": "Ollama",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google",
    }
    p_name = name_map.get(provider_name.lower(), provider_name.capitalize())
    return f"{p_name} · {model_id}"


class LLMRouter:
    """Stateless LLM Router managing provider resolution, retries, and failover chains."""

    def __init__(self) -> None:
        groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.last_active_model: str = format_provider_model("groq", groq_model)

    def resolve_provider_chain(self) -> List[ProviderConfig]:
        """Dynamically build provider chain according to locked LLM policy:
        Development: Groq -> NVIDIA NIM -> Mistral -> Ollama (LOCAL ONLY)
        Production:  Groq -> NVIDIA NIM -> Mistral (Ollama strictly excluded)
        """
        is_prod = is_production_env()

        configs: List[ProviderConfig] = [
            ProviderConfig(
                provider_name="groq",
                model_id=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                display_name="Groq (Primary)",
                api_key=os.getenv("GROQ_API_KEY"),
                base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            ),
            ProviderConfig(
                provider_name="nvidia",
                model_id=os.getenv("NVIDIA_MODEL", os.getenv("NVIDIA_NIM_MODEL", "meta/llama-3.3-70b-instruct")),
                display_name="NVIDIA NIM (Fallback 1)",
                api_key=os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_NIM_API_KEY"),
                base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
            ),
            ProviderConfig(
                provider_name="mistral",
                model_id=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
                display_name="Mistral AI (Fallback 2)",
                api_key=os.getenv("MISTRAL_API_KEY"),
                base_url=os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1"),
            ),
        ]

        # Ollama is strictly local development only — NEVER allow in production
        if not is_prod:
            configs.append(
                ProviderConfig(
                    provider_name="ollama",
                    model_id=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
                    display_name="Ollama Local (Dev Fallback)",
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                )
            )

        return configs

    def invoke(self, messages: List[BaseMessage], **kwargs: Any) -> AIMessage:
        """Synchronously execute chat completion across dynamic provider failover chain."""
        chain = self.resolve_provider_chain()
        if not chain:
            raise RecoverableLLMError("No LLM providers configured or available in failover chain.")

        start_time = time.time()
        attempt_count = 0
        last_error = None

        for idx, config in enumerate(chain):
            attempt_count += 1
            try:
                logger.info(
                    "[LLM-ROUTER] Attempting Provider[%d/%d]: '%s' model='%s'",
                    attempt_count, len(chain), config.provider_name, config.model_id
                )
                provider = ProviderFactory.create_provider(config)
                response = provider.chat(messages, **kwargs)
                self.last_active_model = format_provider_model(config.provider_name, config.model_id)

                total_latency = round((time.time() - start_time) * 1000, 2)
                logger.info(
                    "[LLM-ROUTER] SUCCESS Provider='%s' model='%s' latency=%.2fms retries=%d",
                    config.provider_name, config.model_id, total_latency, attempt_count - 1
                )

                observability_manager.record_llm_usage(
                    model_name=f"{config.provider_name}/{config.model_id}",
                    latency_ms=total_latency,
                )
                return response

            except RecoverableLLMError as exc:
                last_error = str(exc)
                logger.warning(
                    "[LLM-ROUTER] RECOVERABLE FAILURE on Provider='%s' model='%s': %s | Triggering failover...",
                    config.provider_name, config.model_id, exc
                )
                continue
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "[LLM-ROUTER] PRE-TOKEN FAILURE on Provider='%s' model='%s': %s | Triggering failover...",
                    config.provider_name, config.model_id, exc
                )
                continue

        raise RecoverableLLMError(
            f"All LLM providers in failover chain exhausted ({attempt_count} attempts). Last Error: {last_error}"
        )

    def stream(self, messages: List[BaseMessage], **kwargs: Any) -> Generator[str, None, None]:
        """Stream token strings with pre-token failover and mid-stream safety protection."""
        chain = self.resolve_provider_chain()
        if not chain:
            raise RecoverableLLMError("No LLM providers configured or available in failover chain.")

        start_time = time.time()
        attempt_count = 0
        last_error = None

        for idx, config in enumerate(chain):
            attempt_count += 1
            has_emitted_token = False
            try:
                logger.info(
                    "[LLM-ROUTER-STREAM] Attempting Provider[%d/%d]: '%s' model='%s'",
                    attempt_count, len(chain), config.provider_name, config.model_id
                )
                provider = ProviderFactory.create_provider(config)

                for token in provider.stream(messages, **kwargs):
                    has_emitted_token = True
                    self.last_active_model = format_provider_model(config.provider_name, config.model_id)
                    yield token

                total_latency = round((time.time() - start_time) * 1000, 2)
                logger.info(
                    "[LLM-ROUTER-STREAM] STREAM SUCCESS Provider='%s' model='%s' latency=%.2fms",
                    config.provider_name, config.model_id, total_latency
                )
                observability_manager.record_llm_usage(
                    model_name=f"{config.provider_name}/{config.model_id}",
                    latency_ms=total_latency,
                )
                return

            except Exception as exc:
                last_error = str(exc)
                if has_emitted_token:
                    # MID-STREAM SAFETY: Never splice output from another provider if tokens were already emitted!
                    logger.error(
                        "[LLM-ROUTER-STREAM] MID-STREAM FAILURE on Provider='%s': %s | Splicing prevented. Aborting.",
                        config.provider_name, exc
                    )
                    raise
                else:
                    # PRE-TOKEN FAILURE: Pre-token failover allowed
                    logger.warning(
                        "[LLM-ROUTER-STREAM] PRE-TOKEN FAILURE on Provider='%s': %s | Triggering failover...",
                        config.provider_name, exc
                    )
                    continue

        raise RecoverableLLMError(
            f"All LLM providers in stream failover chain exhausted ({attempt_count} attempts). Last Error: {last_error}"
        )

    def health_check(self) -> Dict[str, Any]:
        """Expose health and latency status across provider registry drivers."""
        chain = self.resolve_provider_chain()
        statuses = []
        for config in chain:
            p = ProviderFactory.create_provider(config)
            statuses.append(p.health_check())

        return {
            "status": "healthy" if any(s.get("is_healthy") for s in statuses) else "degraded",
            "provider_chain": statuses,
        }


llm_router = LLMRouter()

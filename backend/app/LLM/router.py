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

from app.Data.database import SessionLocal
from app.LLM.base import (
    ProviderConfig,
    RecoverableLLMError,
    UnrecoverableLLMError,
)
from app.LLM.factory import ProviderFactory
from app.Observability.manager import observability_manager

logger = logging.getLogger(__name__)


class LLMRouter:
    """Stateless LLM Router managing provider resolution, retries, and failover chains."""

    def resolve_provider_chain(self) -> List[ProviderConfig]:
        """Dynamically build provider chain ordered by Model Studio routing_priority."""
        configs: List[ProviderConfig] = []

        try:
            with SessionLocal() as db:
                from app.Models import repository as model_repo
                active_models = model_repo.list_models(db)
                providers_map = {p.id: p for p in model_repo.list_providers(db)}

                # Filter active models and sort by routing_priority
                sorted_models = sorted([m for m in active_models if m.is_active], key=lambda x: x.routing_priority)
                for m in sorted_models:
                    p = providers_map.get(m.provider_id)
                    p_name = p.provider_name if p else "groq"
                    api_key = model_repo.decrypt_api_key(p.encrypted_api_key) if (p and p.encrypted_api_key) else None
                    base_url = p.api_base_url if p else None

                    configs.append(
                        ProviderConfig(
                            provider_name=p_name,
                            model_id=m.model_id,
                            display_name=m.display_name,
                            api_key=api_key or os.getenv("GROQ_API_KEY"),
                            base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                        )
                    )
        except Exception as exc:
            logger.warning("[LLM-ROUTER] Model Studio DB resolution fallback triggered: %s", exc)

        if not configs:
            # Standard default fallback chain: Groq (P1) -> Ollama (P2)
            configs = [
                ProviderConfig(
                    provider_name="groq",
                    model_id="llama-3.3-70b-versatile",
                    display_name="Groq Llama 3.3 70B (Primary)",
                    api_key=os.getenv("GROQ_API_KEY"),
                ),
                ProviderConfig(
                    provider_name="ollama",
                    model_id="qwen2.5:3b",
                    display_name="Ollama Qwen 2.5 3B (Offline Failover)",
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                ),
            ]

        return configs

    def invoke(self, messages: List[BaseMessage], **kwargs: Any) -> AIMessage:
        """Synchronously execute chat completion across dynamic provider failover chain."""
        chain = self.resolve_provider_chain()
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
            except UnrecoverableLLMError as exc:
                logger.error(
                    "[LLM-ROUTER] UNRECOVERABLE FAILURE on Provider='%s' model='%s': %s | Aborting failover.",
                    config.provider_name, config.model_id, exc
                )
                raise exc

        raise RecoverableLLMError(
            f"All LLM providers in failover chain exhausted ({attempt_count} attempts). Last Error: {last_error}"
        )

    def stream(self, messages: List[BaseMessage], **kwargs: Any) -> Generator[str, None, None]:
        """Stream token strings with pre-token failover and mid-stream safety protection."""
        chain = self.resolve_provider_chain()
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

            except RecoverableLLMError as exc:
                last_error = str(exc)
                if has_emitted_token:
                    # MID-STREAM SAFETY: Never splice output from another provider if tokens were already emitted!
                    logger.error(
                        "[LLM-ROUTER-STREAM] MID-STREAM FAILURE on Provider='%s': %s | Splicing prevented. Aborting.",
                        config.provider_name, exc
                    )
                    raise exc
                else:
                    # PRE-TOKEN FAILURE: Pre-token failover allowed
                    logger.warning(
                        "[LLM-ROUTER-STREAM] PRE-TOKEN RECOVERABLE FAILURE on Provider='%s': %s | Triggering failover...",
                        config.provider_name, exc
                    )
                    continue
            except UnrecoverableLLMError as exc:
                logger.error(
                    "[LLM-ROUTER-STREAM] UNRECOVERABLE STREAM FAILURE on Provider='%s': %s",
                    config.provider_name, exc
                )
                raise exc

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

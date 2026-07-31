# backend/app/Models/repository.py
"""
Jarvis AIOS — Repository Data Access Layer for Model Studio.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.Models.models import (
    ProviderConfigModel,
    LLMModelConfigModel,
    RoutingPolicyModel,
    BenchmarkRunModel,
)
from app.Models.adapters import (
    DEFAULT_PROVIDERS,
    DEFAULT_MODELS,
    encrypt_api_key,
)


def seed_default_providers_and_models(db: Session) -> None:
    """Populate default 15+ provider catalog and default models if database is empty."""
    existing = db.execute(select(ProviderConfigModel)).scalars().all()
    if existing:
        return

    provider_map = {}
    for p in DEFAULT_PROVIDERS:
        prov = ProviderConfigModel(
            provider_name=p["name"],
            display_name=p["display"],
            api_base_url=p["url"],
            is_enabled=True,
            is_healthy=True,
            latency_ms=12.5,
        )
        db.add(prov)
        db.flush()
        provider_map[p["name"]] = prov.id

    for m in DEFAULT_MODELS:
        pid = provider_map.get(m["provider_name"])
        if pid:
            model_entry = LLMModelConfigModel(
                provider_id=pid,
                model_id=m["model_id"],
                display_name=m["display_name"],
                context_window=m["context_window"],
                max_output_tokens=m["max_output_tokens"],
                input_cost_per_1k=m["input_cost_per_1k"],
                output_cost_per_1k=m["output_cost_per_1k"],
                is_active=True,
                is_default=m["is_default"],
                routing_priority=m["routing_priority"],
            )
            db.add(model_entry)

    # Add default routing policy
    default_policy = RoutingPolicyModel(
        policy_name="fallback_chain",
        description="Default multi-provider fallback chain (Gemini -> OpenAI -> Anthropic)",
        is_active=True,
        config_json='{"chain": ["gemini-2.5-flash", "gpt-4o", "claude-3-7-sonnet"], "fallback_on_status": [429, 500, 503]}',
    )
    db.add(default_policy)
    db.commit()


# ---------------------------------------------------------------------------
# Provider CRUD
# ---------------------------------------------------------------------------

def list_providers(db: Session) -> List[ProviderConfigModel]:
    seed_default_providers_and_models(db)
    return db.execute(select(ProviderConfigModel).order_by(ProviderConfigModel.id)).scalars().all()


def get_provider_by_name(db: Session, name: str) -> Optional[ProviderConfigModel]:
    return db.execute(
        select(ProviderConfigModel).where(ProviderConfigModel.provider_name == name)
    ).scalar_one_or_none()


def create_or_update_provider(
    db: Session,
    provider_name: str,
    display_name: str,
    api_base_url: str,
    api_key: Optional[str] = None,
    is_enabled: bool = True,
) -> ProviderConfigModel:
    prov = get_provider_by_name(db, provider_name)
    enc_key = encrypt_api_key(api_key) if api_key else (prov.encrypted_api_key if prov else "")

    if prov:
        prov.display_name = display_name
        prov.api_base_url = api_base_url
        if api_key:
            prov.encrypted_api_key = enc_key
        prov.is_enabled = is_enabled
    else:
        prov = ProviderConfigModel(
            provider_name=provider_name,
            display_name=display_name,
            api_base_url=api_base_url,
            encrypted_api_key=enc_key,
            is_enabled=is_enabled,
            is_healthy=True,
            latency_ms=15.0,
        )
        db.add(prov)

    db.commit()
    db.refresh(prov)
    return prov


def delete_provider(db: Session, provider_id: int) -> bool:
    prov = db.execute(
        select(ProviderConfigModel).where(ProviderConfigModel.id == provider_id)
    ).scalar_one_or_none()
    if not prov:
        return False
    db.delete(prov)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Model Config CRUD
# ---------------------------------------------------------------------------

def list_models(db: Session) -> List[LLMModelConfigModel]:
    seed_default_providers_and_models(db)
    return db.execute(select(LLMModelConfigModel).order_by(LLMModelConfigModel.routing_priority)).scalars().all()


def get_model_by_id(db: Session, model_id: str) -> Optional[LLMModelConfigModel]:
    return db.execute(
        select(LLMModelConfigModel).where(LLMModelConfigModel.model_id == model_id)
    ).scalar_one_or_none()


def create_model_config(
    db: Session,
    provider_id: int,
    model_id: str,
    display_name: str,
    context_window: int = 128000,
    max_output_tokens: int = 4096,
    input_cost_per_1k: float = 0.0015,
    output_cost_per_1k: float = 0.0020,
    is_default: bool = False,
    routing_priority: int = 10,
) -> LLMModelConfigModel:
    if is_default:
        db.execute(update(LLMModelConfigModel).values(is_default=False))

    entry = LLMModelConfigModel(
        provider_id=provider_id,
        model_id=model_id,
        display_name=display_name,
        context_window=context_window,
        max_output_tokens=max_output_tokens,
        input_cost_per_1k=input_cost_per_1k,
        output_cost_per_1k=output_cost_per_1k,
        is_active=True,
        is_default=is_default,
        routing_priority=routing_priority,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def set_default_model(db: Session, model_id: str) -> Optional[LLMModelConfigModel]:
    target = get_model_by_id(db, model_id)
    if not target:
        return None
    db.execute(update(LLMModelConfigModel).values(is_default=False))
    target.is_default = True
    db.commit()
    db.refresh(target)
    return target


# ---------------------------------------------------------------------------
# Routing Policy & Benchmark CRUD
# ---------------------------------------------------------------------------

def list_routing_policies(db: Session) -> List[RoutingPolicyModel]:
    seed_default_providers_and_models(db)
    return db.execute(select(RoutingPolicyModel)).scalars().all()


def record_benchmark_run(
    db: Session,
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_latency_ms: float,
    ttft_ms: float,
    status: str = "success",
) -> BenchmarkRunModel:
    run = BenchmarkRunModel(
        model_id=model_id,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_latency_ms=total_latency_ms,
        ttft_ms=ttft_ms,
        status=status,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_benchmark_runs(db: Session, limit: int = 50) -> List[BenchmarkRunModel]:
    return db.execute(
        select(BenchmarkRunModel).order_by(BenchmarkRunModel.id.desc()).limit(limit)
    ).scalars().all()

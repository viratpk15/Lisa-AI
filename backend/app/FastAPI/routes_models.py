# backend/app/FastAPI/routes_models.py
"""
Jarvis AIOS — FastAPI REST Router for Model Studio Subsystem (Sprint 6.6B).

Mount Path: /api/v1/models

Endpoints:
- GET  /api/v1/models/providers
- POST /api/v1/models/providers
- DELETE /api/v1/models/providers/{provider_id}
- GET  /api/v1/models/registry
- POST /api/v1/models/registry
- PATCH /api/v1/models/registry/{model_id}/default
- GET  /api/v1/models/routing-policies
- POST /api/v1/models/benchmark
- POST /api/v1/models/cost-estimate
- GET  /api/v1/models/analytics
- POST /api/v1/models/export
- POST /api/v1/models/import
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.Auth.dependencies import get_current_user
from app.Data.database import get_db
from app.Models import schemas
from app.Models.manager import model_manager, ModelManager

router = APIRouter(prefix="/api/v1/models", tags=["Model Studio"])


def get_model_manager() -> ModelManager:
    return model_manager


# ---------------------------------------------------------------------------
# Provider Registry Endpoints
# ---------------------------------------------------------------------------

@router.get("/providers", response_model=List[schemas.ProviderConfigResponse])
def list_providers(
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """List all registered LLM provider configurations."""
    return manager.list_providers(db)


@router.post("/providers", response_model=schemas.ProviderConfigResponse)
def register_provider(
    payload: schemas.ProviderCreatePayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """Register or update an LLM provider and encrypted API credentials."""
    res = manager.register_provider(
        db=db,
        provider_name=payload.provider_name,
        display_name=payload.display_name,
        api_base_url=payload.api_base_url,
        api_key=payload.api_key,
        is_enabled=payload.is_enabled,
    )
    return schemas.ProviderConfigResponse(**res)


@router.delete("/providers/{provider_id}", response_model=Dict[str, str])
def delete_provider(
    provider_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """Delete a provider configuration by ID."""
    success = manager.delete_provider(db, provider_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
    return {"message": f"Deleted provider {provider_id}"}


# ---------------------------------------------------------------------------
# Model Registry Endpoints
# ---------------------------------------------------------------------------

@router.get("/registry", response_model=List[schemas.LLMModelConfigResponse])
def list_model_registry(
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """List all registered LLM configurations in Model Studio."""
    return manager.list_model_configs(db)


@router.post("/registry", response_model=schemas.LLMModelConfigResponse)
def register_model_config(
    payload: schemas.LLMModelCreatePayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """Register a new LLM model entry."""
    res = manager.create_model_config(
        db=db,
        provider_name=payload.provider_name,
        model_id=payload.model_id,
        display_name=payload.display_name,
        context_window=payload.context_window,
        max_output_tokens=payload.max_output_tokens,
        input_cost_per_1k=payload.input_cost_per_1k,
        output_cost_per_1k=payload.output_cost_per_1k,
        is_default=payload.is_default,
        routing_priority=payload.routing_priority,
    )
    return schemas.LLMModelConfigResponse(**res)


@router.patch("/registry/{model_id}/default", response_model=Dict[str, Any])
def set_default_model(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """Set the system default LLM model."""
    res = manager.set_default_model(db, model_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    return res


# ---------------------------------------------------------------------------
# Routing Policies Endpoints
# ---------------------------------------------------------------------------

@router.get("/routing-policies", response_model=List[schemas.RoutingPolicyResponse])
def list_routing_policies(
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """Fetch routing policies and provider fallback chains."""
    return manager.list_routing_policies(db)


# ---------------------------------------------------------------------------
# Benchmark & Cost Endpoints
# ---------------------------------------------------------------------------

@router.post("/benchmark", response_model=schemas.BenchmarkRunResponse)
def run_model_benchmark(
    payload: schemas.BenchmarkRunPayload,
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """Run an interactive latency & TTFT benchmark on a model."""
    res = manager.run_benchmark(
        db=db,
        model_id=payload.model_id,
        prompt_tokens=payload.prompt_tokens,
        completion_tokens=payload.completion_tokens,
    )
    return schemas.BenchmarkRunResponse(**res)


@router.post("/cost-estimate", response_model=schemas.CostEstimateResponse)
def estimate_model_cost(
    payload: schemas.CostEstimatePayload,
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """Calculate token costs and monthly expenditure projections."""
    res = manager.calculate_cost(
        db=db,
        model_id=payload.model_id,
        prompt_tokens=payload.prompt_tokens,
        completion_tokens=payload.completion_tokens,
        monthly_requests=payload.monthly_requests,
    )
    return schemas.CostEstimateResponse(**res)


# ---------------------------------------------------------------------------
# Analytics, Export & Import Endpoints
# ---------------------------------------------------------------------------

@router.get("/analytics", response_model=schemas.ModelAnalyticsResponse)
def get_model_analytics(
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """Fetch provider health stats, default model, and average latency metrics."""
    res = manager.get_analytics(db)
    return schemas.ModelAnalyticsResponse(**res)


@router.post("/export", response_model=Dict[str, Any])
def export_model_config(
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """Export provider and model configurations."""
    return manager.export_config(db)


@router.post("/import", response_model=Dict[str, Any])
def import_model_config(
    payload: Dict[str, Any] = {},
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    """Import provider and model configurations."""
    return manager.import_config(db, payload)

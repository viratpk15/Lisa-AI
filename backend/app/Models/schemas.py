# backend/app/Models/schemas.py
"""
Jarvis AIOS — Pydantic Schemas for Model Studio REST API.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ProviderConfigResponse(BaseModel):
    id: int
    provider_name: str
    display_name: str
    api_base_url: str
    is_enabled: bool
    is_healthy: bool
    latency_ms: float
    has_api_key: bool
    updated_at: datetime


class ProviderCreatePayload(BaseModel):
    provider_name: str = Field(..., examples=["openai"])
    display_name: str = Field(..., examples=["OpenAI Official"])
    api_base_url: str = Field(..., examples=["https://api.openai.com/v1"])
    api_key: Optional[str] = Field(None, examples=["sk-..."])
    is_enabled: bool = True


class LLMModelConfigResponse(BaseModel):
    id: int
    provider_id: int
    provider_name: str
    model_id: str
    display_name: str
    context_window: int
    max_output_tokens: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    is_active: bool
    is_default: bool
    routing_priority: int
    created_at: datetime


class LLMModelCreatePayload(BaseModel):
    provider_name: str = Field(..., examples=["google"])
    model_id: str = Field(..., examples=["gemini-2.5-flash"])
    display_name: str = Field(..., examples=["Gemini 2.5 Flash"])
    context_window: int = Field(1000000)
    max_output_tokens: int = Field(8192)
    input_cost_per_1k: float = Field(0.0001)
    output_cost_per_1k: float = Field(0.0004)
    is_default: bool = False
    routing_priority: int = 10


class RoutingPolicyResponse(BaseModel):
    id: int
    policy_name: str
    description: Optional[str]
    is_active: bool
    config_json: Dict[str, Any]
    created_at: datetime


class RoutingPolicyCreatePayload(BaseModel):
    policy_name: str
    description: Optional[str] = None
    is_active: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)


class BenchmarkRunResponse(BaseModel):
    id: int
    model_id: str
    prompt_tokens: int
    completion_tokens: int
    total_latency_ms: float
    ttft_ms: float
    status: str
    created_at: datetime


class BenchmarkRunPayload(BaseModel):
    model_id: str = Field(..., examples=["gemini-2.5-flash"])
    prompt_tokens: int = Field(100)
    completion_tokens: int = Field(500)


class CostEstimatePayload(BaseModel):
    model_id: str = Field(..., examples=["gpt-4o"])
    prompt_tokens: int = Field(1000)
    completion_tokens: int = Field(500)
    monthly_requests: int = Field(10000)


class CostEstimateResponse(BaseModel):
    model_id: str
    prompt_cost: float
    completion_cost: float
    total_cost_per_request: float
    estimated_monthly_cost: float


class ModelAnalyticsResponse(BaseModel):
    total_providers: int
    healthy_providers: int
    total_models: int
    default_model: str
    avg_latency_ms: float
    total_benchmark_runs: int

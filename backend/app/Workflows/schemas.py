# backend/app/Workflows/schemas.py
"""
Jarvis AIOS — Pydantic Schemas for Workflow Studio REST API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowNodeData(BaseModel):
    label: str
    node_type: str = Field(..., description="agent, tool, rag, memory, model, condition, parallel, loop, approval, http, transform, code")
    config: Dict[str, Any] = Field(default_factory=dict)


class WorkflowNode(BaseModel):
    id: str
    type: str = "custom"
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    data: WorkflowNodeData


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    condition_expression: Optional[str] = None


class WorkflowDefinitionResponse(BaseModel):
    id: int
    workflow_id: str
    name: str
    description: Optional[str]
    is_active: bool
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    variables: Dict[str, Any]
    definition_json: str
    definition_yaml: Optional[str]
    created_at: datetime
    updated_at: datetime


class WorkflowCreatePayload(BaseModel):
    workflow_id: str = Field(..., examples=["wf_agent_rag_pipeline"])
    name: str = Field(..., examples=["Autonomous Agent & RAG Pipeline"])
    description: Optional[str] = Field(None, examples=["Workflow combining RAG knowledge retrieval and Tool execution"])
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)


class WorkflowCompileResponse(BaseModel):
    workflow_id: str
    is_valid: bool
    node_count: int
    edge_count: int
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    compiled_ast: Dict[str, Any] = Field(default_factory=dict)


class ExecutionTriggerPayload(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict)
    breakpoints: List[str] = Field(default_factory=list)


class ExecutionResponse(BaseModel):
    execution_id: str
    workflow_id: str
    status: str
    started_at: datetime
    stream_url: str


class ResumeExecutionPayload(BaseModel):
    action: str = Field(..., examples=["approve"])  # approve, reject, step
    inputs: Dict[str, Any] = Field(default_factory=dict)


class NodeLogResponse(BaseModel):
    id: int
    node_id: str
    node_type: str
    status: str
    latency_ms: float
    input_json: Dict[str, Any]
    output_json: Dict[str, Any]
    timestamp: datetime


class ExecutionDetailResponse(BaseModel):
    execution_id: str
    workflow_id: str
    status: str
    total_latency_ms: float
    total_tokens: int
    total_cost: float
    started_at: datetime
    completed_at: Optional[datetime]
    logs: List[NodeLogResponse] = Field(default_factory=list)


class WorkflowAnalyticsResponse(BaseModel):
    workflow_id: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_latency_ms: float
    total_tokens: int
    total_cost: float


class TemplateItemResponse(BaseModel):
    template_id: str
    name: str
    description: str
    category: str
    node_count: int

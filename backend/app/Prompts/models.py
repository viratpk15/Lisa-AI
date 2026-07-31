"""
Jarvis AIOS — Prompt Studio Data Models (Pydantic 2.x & SQLAlchemy compatible)
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PromptFolder(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class PromptTag(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    color_hex: str = "#06B6D4"


class Prompt(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    folder_id: Optional[str] = None
    title: str
    description: str = ""
    current_version_id: Optional[str] = None
    is_favorite: bool = False
    is_archived: bool = False
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PromptVersion(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    prompt_id: str
    version_tag: str = "v1.0.0"
    commit_message: str = "Initial version"
    system_prompt: str = ""
    user_prompt: str = ""
    default_model: str = "gpt-4o"
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 2048
    author: str = "System"
    created_at: datetime = Field(default_factory=utc_now)


class PromptVariable(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    prompt_id: str
    var_name: str
    var_type: str = "string"
    default_value: Optional[str] = None
    is_required: bool = True


class PromptExecution(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    prompt_id: str
    version_id: Optional[str] = None
    model_used: str = "gpt-4o"
    input_variables: Dict[str, Any] = Field(default_factory=dict)
    raw_output: str = ""
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0
    status: str = "SUCCESS"
    executed_at: datetime = Field(default_factory=utc_now)


class PromptEvaluation(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    execution_id: str
    correctness_score: float = 10.0
    hallucination_score: float = 0.0
    tone_score: float = 9.5
    clarity_score: float = 9.5
    relevance_score: float = 10.0
    evaluator_type: str = "AI_AUTOMATED"
    detailed_feedback: Dict[str, Any] = Field(default_factory=dict)
    evaluated_at: datetime = Field(default_factory=utc_now)


class PromptTemplate(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    category: str
    description: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    default_variables: Dict[str, Any] = Field(default_factory=dict)

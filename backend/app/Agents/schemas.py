# backend/app/Agents/schemas.py
"""Pydantic v2 schemas for Agent Studio API.

Used in FastAPI routers for request validation and OpenAPI generation.
All `Read` schemas use `from_attributes=True` (Pydantic v2) for ORM compatibility.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class AgentCreate(BaseModel):
    name: str = Field(..., description="Human readable agent name")
    description: Optional[str] = Field(None, description="Long description")


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, description="New name")
    description: Optional[str] = Field(None, description="New description")
    is_active: Optional[bool] = Field(None, description="Soft delete flag")


class AgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# AgentVersion
# ---------------------------------------------------------------------------

class AgentVersionCreate(BaseModel):
    agent_id: int = Field(..., description="Parent agent ID")
    version_number: int = Field(..., description="Version number")
    changelog: Optional[str] = Field(None, description="Human readable change log")


class AgentVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_id: int
    version_number: int
    changelog: Optional[str]
    is_current: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------

class TeamNodeCreate(BaseModel):
    agent_version_id: int
    position_x: float = 0.0
    position_y: float = 0.0


class TeamEdgeCreate(BaseModel):
    source_node_id: int
    target_node_id: int
    condition_json: Optional[str] = None


class AgentTeamCreate(BaseModel):
    agent_id: int
    name: str
    nodes: List[TeamNodeCreate]
    edges: List[TeamEdgeCreate]


class AgentTeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_id: int
    name: str
    nodes: List[dict]
    edges: List[dict]


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

class ExecutionCreate(BaseModel):
    version_id: int = Field(..., description="Agent version to execute")
    input_payload: Optional[dict] = Field(None, description="Initial input for the execution")


class ExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_id: int
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    run_id: Optional[str]

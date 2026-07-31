"""
Jarvis AIOS — Multi-Agent Task Model
------------------------------------

Generic task model for Multi-Agent Supervisor task creation, assignment,
dependency tracking, and status management.
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Execution status enum for Multi-Agent tasks."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentTask(BaseModel):
    """Generic task unit assigned by Supervisor to Worker Agents."""

    task_id: str = Field(..., description="Unique task identifier.")
    objective: str = Field(..., description="Clear objective / goal description.")
    assigned_agent: str = Field(..., description="Target worker agent ID (e.g. 'researcher', 'coder', 'document_agent').")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status.")
    priority: int = Field(default=1, description="Task execution priority (higher runs first).")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs that must complete first.")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp.")
    completed_at: Optional[str] = Field(default=None, description="Completion timestamp.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary task metadata.")

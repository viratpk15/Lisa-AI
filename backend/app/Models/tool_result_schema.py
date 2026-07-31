"""
Jarvis AIOS — Standard Tool Result & Execution Record Schema
-------------------------------------------------------------

Standardized execution record schema used by all worker agents for team scratchpad entries.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field


class ToolExecutionRecord(BaseModel):
    """Standardized tool and worker agent execution record."""

    task_id: str = Field(..., description="Target task ID.")
    agent: str = Field(..., description="Executing worker agent ID.")
    tool: str = Field(default="internal_reasoning", description="Tool or component used.")
    input: Union[Dict[str, Any], str] = Field(default_factory=dict, description="Input parameters/query.")
    output: Union[Dict[str, Any], str] = Field(..., description="Output content or dictionary result.")
    duration_ms: float = Field(default=0.0, description="Execution duration in milliseconds.")
    success: bool = Field(default=True, description="Whether execution succeeded.")
    citations: List[Dict[str, Any]] = Field(default_factory=list, description="Preserved evidence citations.")
    artifacts: List[Dict[str, Any]] = Field(default_factory=list, description="Generated artifacts/files.")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Execution timestamp.",
    )

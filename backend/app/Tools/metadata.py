"""
Jarvis AIOS
--------------------
Tool Metadata & Standardized ToolResult Schemas

Single source of truth for tool definitions, capabilities,
permission levels, and provider-independent execution results.
"""

from enum import Enum
from typing import Any, List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PermissionLevel(str, Enum):
    """Access control permission levels for tool execution."""
    PUBLIC = "PUBLIC"
    USER = "USER"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"
    INTERNAL = "INTERNAL"


class ExecutionStatus(str, Enum):
    """Standardized tool execution status flags."""
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    PERMISSION_DENIED = "PERMISSION_DENIED"


class ToolMetadata(BaseModel):
    """
    Comprehensive single source of truth for tool discovery, validation,
    documentation, and LLM schema binding.
    """
    name: str
    display_name: str = ""
    description: str = ""
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
    author: str = "Jarvis AIOS Core"
    permission_level: PermissionLevel = PermissionLevel.USER
    requires_approval: bool = False
    enabled: bool = True
    timeout_seconds: float = 30.0
    supports_streaming: bool = False
    supports_async: bool = True
    supports_parallel: bool = True
    supports_cancellation: bool = False
    parameter_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    icon: str = "Wrench"
    documentation_url: str = ""

    def model_post_init(self, __context: Any) -> None:
        """Set default display name if empty."""
        if not self.display_name:
            self.display_name = self.name.replace("_", " ").title()


class ToolResult(BaseModel):
    """
    Standardized, provider-independent return object for all ToolEngine executions.
    Never return raw un-normalized objects from the ToolEngine gate.
    """
    tool_name: str
    execution_id: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: datetime
    duration_ms: float
    output: Any = None
    structured_output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ToolResult to a standard dictionary."""
        return self.model_dump(mode="json")

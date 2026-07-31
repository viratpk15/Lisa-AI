"""
Jarvis AIOS
-----------
Agent Configuration Model

Pydantic model for agent configuration. Used to define agent identity
and enabled state. Future implementations may extend this with additional
configuration fields like capabilities, routes, or custom parameters.
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for an agent.

    Defines identity, metadata, allowed tools, model preference, and execution limits.
    """

    id: str = Field(default="", description="Unique agent string ID (e.g. 'researcher', 'coder').")
    name: str = Field(..., min_length=1, description="Unique agent identifier.")
    description: str = Field(
        default="", description="Human-readable description of agent capabilities."
    )
    enabled: bool = Field(default=True, description="Whether the agent is active.")
    capabilities: List[str] = Field(default_factory=list, description="Capabilities list.")
    allowed_tools: List[str] = Field(default_factory=list, description="Subset of allowed tool names.")
    model_preference: str = Field(default="gpt-4o", description="Preferred model for this agent.")
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "backoff": "exponential"}, description="Retry policy config.")
    timeout: float = Field(default=60.0, description="Agent execution timeout in seconds.")

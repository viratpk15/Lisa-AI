"""
Jarvis AIOS
-----------
MCP Configuration Models

Pydantic models for MCP server configuration validation.
Provides structured configuration that can be loaded from environment
variables or configuration files.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MCPServerConfigModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1, description="Unique server identifier")
    description: str = Field(default="", description="Server description")
    enabled: bool = Field(default=True, description="Whether server is enabled")
    command: Optional[str] = Field(default=None, description="Launch command")
    args: list[str] = Field(default_factory=list, description="Launch arguments")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    timeout: int = Field(default=30, ge=1, le=300, description="Execution timeout in seconds")


class MCPConfigModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    servers: list[MCPServerConfigModel] = Field(
        default_factory=list,
        description="List of MCP server configurations"
    )
    auto_register: bool = Field(
        default=False,
        description="Auto-register servers on startup"
    )

    def get_enabled_servers(self) -> list[MCPServerConfigModel]:
        """Get list of enabled server configurations.

        Returns:
            List of servers where enabled=True.
        """
        return [s for s in self.servers if s.enabled]

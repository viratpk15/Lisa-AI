"""
Jarvis AIOS — MCP Server Health Monitor
---------------------------------------

Lightweight internal health monitor for tracking MCP server connections, status,
latency, and available tools.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field


class MCPServerHealth(BaseModel):
    """Health metrics model for an MCP server."""

    server_id: str = Field(..., description="Target server ID.")
    status: Literal["online", "offline", "error"] = Field(default="offline", description="Server status.")
    latency_ms: float = Field(default=0.0, description="Ping latency in milliseconds.")
    version: str = Field(default="1.0.0", description="MCP server protocol version.")
    last_seen: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last health check timestamp.",
    )
    available_tools: List[str] = Field(default_factory=list, description="List of tools exposed by this server.")
    authenticated: bool = Field(default=True, description="Whether connector has valid auth credentials.")
    rate_limit_status: str = Field(default="ok", description="Rate limit status.")
    workspace_valid: bool = Field(default=True, description="Whether filesystem workspace path is valid.")
    workspace_root: str = Field(default="workspace", description="Configured workspace root path.")
    permissions: str = Field(default="read/write", description="Connector permission level.")


class MCPHealthMonitor:
    """Internal monitor tracking health status for registered MCP servers."""

    def __init__(self) -> None:
        self._health_records: Dict[str, MCPServerHealth] = {}

    def update_health(
        self,
        server_id: str,
        status: Literal["online", "offline", "error"],
        latency_ms: float = 0.0,
        version: str = "1.0.0",
        tools: List[str] | None = None,
    ) -> MCPServerHealth:
        """Update or record server health status."""
        health = MCPServerHealth(
            server_id=server_id,
            status=status,
            latency_ms=round(latency_ms, 2),
            version=version,
            last_seen=datetime.now(timezone.utc).isoformat(),
            available_tools=tools or [],
        )
        self._health_records[server_id] = health
        return health

    def get_health(self, server_id: str) -> MCPServerHealth | None:
        """Get health record for a specific server."""
        return self._health_records.get(server_id)

    def get_all_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health dictionary summary for all servers."""
        return {sid: record.model_dump() for sid, record in self._health_records.items()}


_monitor_instance: MCPHealthMonitor | None = None


def get_mcp_health_monitor() -> MCPHealthMonitor:
    """Get the global health monitor singleton instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = MCPHealthMonitor()
    return _monitor_instance

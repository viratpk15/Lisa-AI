"""
Jarvis AIOS — Unified Tool Interface
------------------------------------

Common abstraction unifying Native Tools and MCP Tools into a single interface.
Inherits from base `Tool` to ensure 100% backward compatibility with Tool Engine.
"""

from typing import Any, Dict, Optional
from app.Tools.tool import Tool
from app.Tools.metadata import ToolMetadata, PermissionLevel


class UnifiedTool(Tool):
    """Unified Tool interface wrapping Native or MCP tools identically."""

    def __init__(
        self,
        tool_id: str,
        name: str,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[ToolMetadata] = None,
        is_mcp: bool = False,
        mcp_server_id: Optional[str] = None,
    ) -> None:
        self.tool_id = tool_id
        self.is_mcp = is_mcp
        self.mcp_server_id = mcp_server_id

        meta = metadata or ToolMetadata(
            name=name,
            description=description,
            permission_level=PermissionLevel.USER,
            parameter_schema=parameters or {"type": "object", "properties": {}, "required": []},
        )
        super().__init__(metadata=meta)

    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool. Must be overridden by subclasses/adapters."""
        raise NotImplementedError("UnifiedTool subclasses must implement execute().")

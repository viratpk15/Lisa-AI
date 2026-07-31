"""
Jarvis AIOS — MCP Tool Adapter
------------------------------

Adapts MCP tools into the UnifiedTool interface used by Tool Engine.
Worker Dispatcher calls all tools identically without needing to know whether
they are Native or MCP tools.
"""

import logging
from typing import Any, Dict, Optional
from app.Tools.unified_tool import UnifiedTool
from app.Tools.metadata import ToolMetadata, PermissionLevel

logger = logging.getLogger(__name__)


class MCPToolAdapter(UnifiedTool):
    """Adapter class converting an MCP tool definition into a standard Tool."""

    def __init__(
        self,
        client_name: str,
        tool_name: str,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        permission_level: PermissionLevel = PermissionLevel.USER,
    ) -> None:
        self.client_name = client_name
        self.tool_name = tool_name

        meta = ToolMetadata(
            name=tool_name,
            description=description or f"MCP Tool '{tool_name}' provided by server '{client_name}'.",
            permission_level=permission_level,
            parameter_schema=parameters or {"type": "object", "properties": {}, "required": []},
        )

        super().__init__(
            tool_id=f"mcp_{client_name}_{tool_name}",
            name=tool_name,
            description=meta.description,
            parameters=meta.parameter_schema,
            metadata=meta,
            is_mcp=True,
            mcp_server_id=client_name,
        )

    def execute(self, **kwargs: Any) -> Any:
        """Execute the adapted MCP tool through MCPManager."""
        from app.MCP.mcp_manager import get_mcp_manager
        logger.info("[MCP-ADAPTER] Executing MCP Tool '%s' on server '%s'", self.tool_name, self.client_name)
        manager = get_mcp_manager()
        return manager.execute_tool(self.client_name, self.tool_name, **kwargs)

"""
Jarvis AIOS — MCP Configuration Loader
--------------------------------------

Configuration-driven MCP server loader supporting environment variables,
dictionary configs, and JSON files.
"""

import os
import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class MCPServerConfigModel(BaseModel):
    """Configuration for an MCP server."""

    server_id: str = Field(..., description="Unique server ID (e.g. 'github_mcp', 'filesystem_mcp').")
    server_name: str = Field(..., description="Human-readable server name.")
    version: str = Field(default="1.0.0", description="Server version.")
    description: str = Field(default="", description="Server capabilities summary.")
    transport: str = Field(default="stdio", description="Transport type ('stdio', 'sse', 'inprocess').")
    enabled: bool = Field(default=True, description="Whether server is active.")
    connection_params: Dict[str, Any] = Field(default_factory=dict, description="Custom connection options.")
    available_tools: List[str] = Field(default_factory=list, description="Exposed tools list.")


def load_mcp_configurations() -> List[MCPServerConfigModel]:
    """Load MCP server configs from environment or fallback defaults."""
    config_json = os.environ.get("JARVIS_MCP_SERVERS_JSON")
    configs: List[MCPServerConfigModel] = []

    if config_json:
        try:
            raw_list = json.loads(config_json)
            for item in raw_list:
                configs.append(MCPServerConfigModel(**item))
            return configs
        except Exception:
            pass

    # Built-in configuration defaults
    default_servers = [
        {
            "server_id": "browser_mcp",
            "server_name": "BrowserMCP",
            "version": "1.0.0",
            "description": "Browser automation and web search server",
            "transport": "inprocess",
            "enabled": True,
            "available_tools": ["search_web", "navigate_page", "extract_html"],
        },
        {
            "server_id": "github_mcp",
            "server_name": "GitHubMCP",
            "version": "1.0.0",
            "description": "GitHub repository and issue operations server",
            "transport": "inprocess",
            "enabled": True,
            "available_tools": ["get_repository", "list_issues", "create_pull_request"],
        },
        {
            "server_id": "filesystem_mcp",
            "server_name": "FilesystemMCP",
            "version": "1.0.0",
            "description": "Filesystem read/write operations server",
            "transport": "inprocess",
            "enabled": True,
            "available_tools": ["read_file", "write_file", "list_directory"],
        },
    ]

    return [MCPServerConfigModel(**item) for item in default_servers]

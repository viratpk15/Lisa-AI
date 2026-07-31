"""
Jarvis AIOS
-----------
MCP Foundation

Model Context Protocol integration for pluggable MCP servers.
This module provides the abstraction layer for future MCP server implementations.
The current tool execution flow remains unchanged - MCP servers will integrate
through the Tool Engine without modifying existing tools.
"""

# MCP client interface
from app.MCP.client import MCPClient, MCPServerConfig

# MCP registry for managing servers
from app.MCP.registry import MCPRegistry

# MCP configuration models (Pydantic models for validation)
from app.MCP.models import MCPServerConfigModel, MCPConfigModel

# MCP server implementations
from app.MCP.servers import FilesystemMCPClient, BrowserMCPClient, GitHubMCPClient

__all__ = [
    "MCPClient",
    "MCPServerConfig",
    "MCPRegistry",
    "MCPServerConfigModel",
    "MCPConfigModel",
    "FilesystemMCPClient",
    "BrowserMCPClient",
    "GitHubMCPClient",
    "get_mcp_registry",
    "get_filesystem_server",
    "get_browser_server",
    "get_github_server",
]

# Global MCP registry instance
mcp_registry: MCPRegistry | None = None

# Global Filesystem MCP client instance
_filesystem_client: FilesystemMCPClient | None = None

# Global Browser MCP client instance
_browser_client: BrowserMCPClient | None = None

# Global GitHub MCP client instance
_github_client: GitHubMCPClient | None = None


def get_mcp_registry() -> MCPRegistry:
    """Get or create the global MCP registry instance.

    Returns:
        The global MCPRegistry singleton.
    """
    global mcp_registry
    if mcp_registry is None:
        mcp_registry = MCPRegistry()
    return mcp_registry


def get_filesystem_server() -> FilesystemMCPClient:
    """Get or create the global Filesystem MCP client instance.

    Returns:
        The global FilesystemMCPClient singleton.
    """
    global _filesystem_client
    if _filesystem_client is None:
        _filesystem_client = FilesystemMCPClient()
    return _filesystem_client


def get_browser_server() -> BrowserMCPClient:
    """Get or create the global Browser MCP client instance.

    Returns:
        The global BrowserMCPClient singleton.
    """
    global _browser_client
    if _browser_client is None:
        _browser_client = BrowserMCPClient()
    return _browser_client


def get_github_server() -> GitHubMCPClient:
    """Get or create the global GitHub MCP client instance.

    Returns:
        The global GitHubMCPClient singleton.
    """
    global _github_client
    if _github_client is None:
        _github_client = GitHubMCPClient()
    return _github_client

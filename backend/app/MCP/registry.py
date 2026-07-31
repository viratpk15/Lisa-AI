"""
Jarvis AIOS
-----------
MCP Registry

Registry for MCP (Model Context Protocol) clients.
Provides a pluggable mechanism for MCP servers to register themselves
with the Jarvis runtime without modifying existing tool execution flow.

Usage for future MCP servers:

    # 1. Create a client implementing MCPClient
    class FileSystemMCPClient(MCPClient):
        ...

    # 2. Register with the registry
    registry.register(FileSystemMCPClient(MCPServerConfig(name="filesystem")))

    # 3. Later, tools can be accessed through the registry
    tools = registry.list_all_tools()
    # Returns: {"calculator", "datetime", ...} plus MCP tools when integrated
"""

from typing import Any

from app.MCP.client import MCPClient, MCPServerConfig


class MCPRegistry:
    """Registry for MCP clients.

    Manages MCP server lifecycle and provides lookup capabilities.
    Follows the same pattern as ToolRegistry for consistency.

    MCP servers register here to make their tools available.
    The registry does NOT modify existing tools - it only tracks
    MCP clients for future integration.
    """

    def __init__(self) -> None:
        """Initialize the registry with an empty client list."""
        self._clients: dict[str, MCPClient] = {}

    def register(self, client: MCPClient) -> None:
        """Register an MCP client.

        Args:
            client: An MCPClient instance to register.

        Raises:
            ValueError: If a client with the same name is already registered.
        """
        config = client.config
        if not config.enabled:
            return  # Silently skip disabled servers

        if config.name in self._clients:
            raise ValueError(
                f"MCP client '{config.name}' is already registered."
            )

        # Initialize the client (connect to server, load tools, etc.)
        client.initialize()
        self._clients[config.name] = client

    def unregister(self, name: str) -> None:
        """Unregister an MCP client by name.

        Args:
            name: The name of the client to remove.

        Raises:
            ValueError: If no client with the given name exists.
        """
        if name not in self._clients:
            raise ValueError(f"MCP client '{name}' is not registered.")

        client = self._clients[name]
        client.shutdown()
        del self._clients[name]

    def get(self, name: str) -> MCPClient:
        """Get a registered MCP client by name.

        Args:
            name: The name of the client to retrieve.

        Returns:
            The MCPClient instance.

        Raises:
            ValueError: If no client with the given name exists.
        """
        if name not in self._clients:
            raise ValueError(f"MCP client '{name}' is not registered.")

        return self._clients[name]

    def list_clients(self) -> list[MCPServerConfig]:
        """List all registered MCP client configurations.

        Returns:
            List of MCPServerConfig for all registered clients.
        """
        return [client.config for client in self._clients.values()]

    def list_tools(self, client_name: str) -> list[str]:
        """List tools provided by a specific MCP client.

        Args:
            client_name: The name of the client.

        Returns:
            List of tool names provided by the client.

        Raises:
            ValueError: If no client with the given name exists.
        """
        client = self.get(client_name)
        return client.list_tools()

    def list_all_tools(self) -> list[str]:
        """List all tools provided by all registered MCP clients.

        Returns:
            List of tool names from all clients (deduplicated).
        """
        tools: set[str] = set()
        for client in self._clients.values():
            tools.update(client.list_tools())
        return sorted(tools)

    def execute_tool(self, client_name: str, tool_name: str, **kwargs: Any) -> Any:
        """Execute a tool on a registered MCP client.

        Args:
            client_name: The name of the MCP client.
            tool_name: The name of the tool to execute.
            **kwargs: Arguments to pass to the tool.

        Returns:
            The tool execution result.

        Raises:
            ValueError: If the client or tool is not found.
        """
        client = self.get(client_name)
        return client.execute_tool(tool_name, **kwargs)

    def has_client(self, name: str) -> bool:
        """Check if a client is registered.

        Args:
            name: The client name to check.

        Returns:
            True if the client is registered, False otherwise.
        """
        return name in self._clients

    def clear(self) -> None:
        """Remove all registered clients and shut them down."""
        for client in self._clients.values():
            client.shutdown()
        self._clients.clear()


# Global registry instance (will be lazily initialized via get_mcp_registry)
mcp_registry: MCPRegistry | None = None

"""
Jarvis AIOS
-----------
MCP Client Interface

Abstract base class for MCP (Model Context Protocol) clients.
MCP servers will implement this interface to provide their capabilities
to Jarvis AIOS. The interface follows the same pattern as the existing
Tool abstraction, ensuring consistency across the codebase.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server.

    Used to define connection parameters for MCP servers.
    Future implementations may use this to connect to external MCP services.

    Attributes:
        name: Unique identifier for the MCP server.
        description: Human-readable description of the server's capabilities.
        enabled: Whether the server is currently active.
        capabilities: List of capability names this server provides.
    """

    name: str
    description: str = ""
    enabled: bool = True
    capabilities: list[str] = None  # type: ignore

    def __post_init__(self) -> None:
        """Initialize default capabilities list if not provided."""
        if self.capabilities is None:
            self.capabilities = []


class MCPClient(ABC):
    """Abstract base class for MCP (Model Context Protocol) clients.

    Every MCP server implementation must inherit from this class.
    The interface provides a consistent way for MCP servers to expose
    their tools and resources to the Jarvis runtime.

    MCP clients are designed to be registered in the MCPRegistry and
    accessed through the Tool Engine without modifying existing code.

    Example implementation:

        class MyMCPClient(MCPClient):
            def __init__(self, config: MCPServerConfig):
                self._config = config
                self._tools = {}  # Populate with server's tools

            def list_tools(self) -> list[str]:
                return list(self._tools.keys())

            def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
                if tool_name in self._tools:
                    return self._tools[tool_name].execute(**kwargs)
                raise ValueError(f"Unknown tool: {tool_name}")

            def initialize(self) -> None:
                # Connect to MCP server, load tools, etc.
                pass

            def shutdown(self) -> None:
                # Clean up resources
                pass
    """

    @property
    @abstractmethod
    def config(self) -> MCPServerConfig:
        """Get the server configuration.

        Returns:
            The MCPServerConfig for this client.
        """
        raise NotImplementedError

    @abstractmethod
    def list_tools(self) -> list[str]:
        """List available tool names from this MCP server.

        Returns:
            List of tool names available on this server.
        """
        raise NotImplementedError

    @abstractmethod
    def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a tool on this MCP server.

        Args:
            tool_name: Name of the tool to execute.
            **kwargs: Arguments to pass to the tool.

        Returns:
            The tool execution result.

        Raises:
            ValueError: If the tool is not found or arguments are invalid.
        """
        raise NotImplementedError

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the MCP client and connect to the server.

        This method is called when the client is registered.
        Implementations should establish connections and load tool metadata.
        """
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the MCP client and clean up resources.

        This method is called when the client is unregistered or
        the application shuts down.
        """
        raise NotImplementedError

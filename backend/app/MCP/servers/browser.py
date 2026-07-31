"""
Jarvis AIOS
-----------
Browser MCP Server

Read-only web browsing through the Model Context Protocol.
Provides search_web and fetch_page tools with mocked responses
for provider-agnostic implementation.
"""

from typing import Any

from app.MCP.client import MCPClient, MCPServerConfig


# Maximum content size in bytes (1 MB).
_MAX_CONTENT_SIZE_BYTES: int = 1_000_000


class BrowserMCPClient(MCPClient):
    """Browser MCP server with read-only web access.

    Provides search_web and fetch_page tools for web browsing.
    Uses mocked responses for now - can be replaced with real
    provider implementations (duckduckgo, serpapi, etc.) later.
    """

    def __init__(self, config: MCPServerConfig | None = None) -> None:
        """Initialize the Browser MCP client.

        Args:
            config: Optional MCP server configuration. If not provided,
                a default configuration is used.
        """
        self._config = config or MCPServerConfig(
            name="browser",
            description="Read-only web browsing via MCP.",
            enabled=True,
            capabilities=["search_web", "fetch_page"]
        )
        self._tools: dict[str, Any] = {}

    @property
    def config(self) -> MCPServerConfig:
        """Get the server configuration.

        Returns:
            The MCPServerConfig for this client.
        """
        return self._config

    def list_tools(self) -> list[str]:
        """List available tool names from this MCP server.

        Returns:
            List of tool names available on this server.
        """
        return list(self._tools.keys())

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
        if tool_name == "search_web":
            return self._search_web(**kwargs)
        elif tool_name == "fetch_page":
            return self._fetch_page(**kwargs)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def initialize(self) -> None:
        """Initialize the MCP client and connect to the server."""
        self._tools = {
            "search_web": self._search_web,
            "fetch_page": self._fetch_page,
        }

    def shutdown(self) -> None:
        """Shutdown the MCP client and clean up resources."""
        self._tools.clear()

    def _search_web(self, **kwargs: Any) -> list[dict[str, str]]:
        """Search the web for a query.

        Args:
            query: The search query string.

        Returns:
            List of search results with 'title', 'url', and 'snippet' keys.

        Raises:
            ValueError: If query is missing or invalid.
        """
        query = kwargs.get("query")

        if query is None:
            raise ValueError(
                "Missing 'query' argument. Provide a search query as a string."
            )

        if not isinstance(query, str):
            raise ValueError("The 'query' argument must be a string.")

        if not query.strip():
            raise ValueError("The 'query' argument must be a non-empty string.")

        # Mock search results - provider-agnostic implementation
        # These can be replaced with real search provider calls later
        return [
            {
                "title": f"Mock Result: {query}",
                "url": f"https://example.com/search?q={query.replace(' ', '+')}",
                "snippet": f"This is a mock search result for '{query}'. "
                           "Replace with real web search provider.",
                "mock": True,
                "provider": "browser-mcp"
            },
            {
                "title": f"Another Mock Result: {query}",
                "url": f"https://example.org/search?q={query.replace(' ', '+')}",
                "snippet": f"Additional mock result for '{query}' with more context.",
                "mock": True,
                "provider": "browser-mcp"
            }
        ]

    def _fetch_page(self, **kwargs: Any) -> str:
        """Fetch the content of a web page.

        Args:
            url: The URL to fetch.

        Returns:
            The page content as a string.

        Raises:
            ValueError: If url is missing or invalid.
        """
        url = kwargs.get("url")

        if url is None:
            raise ValueError(
                "Missing 'url' argument. Provide a URL as a string."
            )

        if not isinstance(url, str):
            raise ValueError("The 'url' argument must be a string.")

        if not url.strip():
            raise ValueError("The 'url' argument must be a non-empty string.")

        # Basic URL validation - must start with http/https
        if not url.startswith(("http://", "https://")):
            raise ValueError(
                "Invalid URL. Must start with 'http://' or 'https://'."
            )

        # Mock page content - provider-agnostic implementation
        # These can be replaced with real HTTP fetch calls later
        # Returns content with mock metadata for distinguishing responses
        return f"Mock page content for {url}\n\n" \
               f"metadata: {{'mock': true, 'provider': 'browser-mcp'}}\n\n" \
               f"This is a mock response. Replace with real web page fetch " \
               f"using a provider like requests or aiohttp in production."

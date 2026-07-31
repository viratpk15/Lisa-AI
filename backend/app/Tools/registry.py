"""
Jarvis AIOS
--------------------
Tool Registry & Discovery Engine

Central repository for tool registration, dynamic discovery, search,
category management, and LLM schema generation without unnecessary instantiation.
"""

from typing import Dict, List, Optional, Any

from app.Tools.tool import Tool
from app.Tools.metadata import ToolMetadata, PermissionLevel
from app.Tools.calculator import CalculatorTool
from app.Tools.datetime_tool import DateTimeTool
from app.Tools.file_reader import FileReaderTool
from app.Tools.python_runner import PythonRunnerTool
from app.Tools.filesystem_tool import FilesystemTool
from app.Tools.terminal_tool import TerminalTool
from app.Tools.git_tool import GitTool
from app.Tools.web_search_tool import WebSearchTool
from app.Tools.browser_tool import BrowserTool


class ToolRegistry:
    """
    Stores and indexes registered tools.
    Supports dynamic registration, metadata search, discovery, and schema exports.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

        # Register default builtin tools
        self.register(CalculatorTool())
        self.register(DateTimeTool())
        self.register(FileReaderTool())
        self.register(PythonRunnerTool())
        self.register(FilesystemTool())
        self.register(TerminalTool())
        self.register(GitTool())
        self.register(WebSearchTool())
        self.register(BrowserTool())

    def register(self, tool: Tool) -> None:
        """Register a tool instance."""
        if not isinstance(tool, Tool):
            raise TypeError(f"Registered object must inherit from Tool. Received {type(tool).__name__}.")

        name = tool.metadata.name
        if not name:
            raise ValueError("Tool name must not be empty.")

        self._tools[name] = tool

    def unregister(self, name: str) -> None:
        """Unregister a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered.")
        del self._tools[name]

    def get(self, name: str) -> Tool:
        """Retrieve a registered tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered.")
        return self._tools[name]

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered by name."""
        return name in self._tools

    def list_tools(self) -> List[Tool]:
        """Return list of all registered Tool instances."""
        return list(self._tools.values())

    def discover(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        permission_level: Optional[PermissionLevel] = None,
        enabled_only: bool = True,
    ) -> List[ToolMetadata]:
        """
        Discover tools by category, tag, or permission level without instantiating objects.

        Returns:
            List of ToolMetadata objects matching filter criteria.
        """
        results: List[ToolMetadata] = []

        for tool in self._tools.values():
            meta = tool.metadata

            if enabled_only and not meta.enabled:
                continue

            if category and meta.category.lower() != category.lower():
                continue

            if tag and tag.lower() not in [t.lower() for t in meta.tags]:
                continue

            if permission_level and meta.permission_level != permission_level:
                continue

            results.append(meta)

        return results

    def search(self, query: str, enabled_only: bool = True) -> List[ToolMetadata]:
        """
        Perform case-insensitive search across tool names, display names, and descriptions.
        """
        if not query:
            return self.discover(enabled_only=enabled_only)

        q = query.lower().strip()
        matches: List[ToolMetadata] = []

        for tool in self._tools.values():
            meta = tool.metadata
            if enabled_only and not meta.enabled:
                continue

            if (
                q in meta.name.lower()
                or q in meta.display_name.lower()
                or q in meta.description.lower()
                or any(q in t.lower() for t in meta.tags)
            ):
                matches.append(meta)

        return matches

    def categories(self) -> List[str]:
        """Return sorted list of unique tool categories."""
        cats = {tool.metadata.category for tool in self._tools.values()}
        return sorted(cats)

    def schemas(self, names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Export JSON Schema representations for all or specified tools for LLM binding.
        """
        if names:
            tools = [self.get(name) for name in names if name in self._tools]
        else:
            tools = list(self._tools.values())

        return [tool.to_schema() for tool in tools if tool.metadata.enabled]


registry = ToolRegistry()

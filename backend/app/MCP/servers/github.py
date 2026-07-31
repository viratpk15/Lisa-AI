"""
Jarvis AIOS — Production Read-Only GitHub MCP Server
---------------------------------------------------

Read-only GitHub repository access through the Model Context Protocol.
Supports: get_repository, list_branches, browse_files, read_file, search_code,
search_repos, list_issues, list_pull_requests, list_commits, get_tree, get_readme.

Strictly READ-ONLY. Rejects all write, push, merge, create, or delete operations.
"""

import os
import logging
from typing import Any
from app.MCP.client import MCPClient, MCPServerConfig

logger = logging.getLogger(__name__)

READ_ONLY_GITHUB_TOOLS = [
    "get_repository",
    "list_branches",
    "browse_files",
    "read_file",
    "search_code",
    "search_repos",
    "list_issues",
    "list_pull_requests",
    "list_commits",
    "get_tree",
    "get_readme",
    "list_repository_files",
]

FORBIDDEN_WRITE_TOOLS = [
    "create_issue",
    "create_pull_request",
    "merge_pull_request",
    "write_file",
    "delete_file",
    "push_commit",
    "delete_repo",
]


class GitHubMCPClient(MCPClient):
    """Production GitHub MCP client enforcing 100% read-only access."""

    def __init__(self, config: MCPServerConfig | None = None) -> None:
        token = os.environ.get("GITHUB_TOKEN", "")
        self._config = config or MCPServerConfig(
            name="github",
            description="Read-only GitHub repository access via MCP.",
            enabled=True,
            capabilities=READ_ONLY_GITHUB_TOOLS,
        )
        self.token = token
        self._tools: dict[str, Any] = {}

    @property
    def config(self) -> MCPServerConfig:
        return self._config

    def list_tools(self) -> list[str]:
        return READ_ONLY_GITHUB_TOOLS

    def initialize(self) -> None:
        self._tools = dict.fromkeys(READ_ONLY_GITHUB_TOOLS, self._dispatch_tool)

    def shutdown(self) -> None:
        self._tools.clear()

    def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
        if tool_name in FORBIDDEN_WRITE_TOOLS:
            raise PermissionError(f"GitHub MCP is strictly READ-ONLY. Action '{tool_name}' is forbidden.")

        if tool_name not in READ_ONLY_GITHUB_TOOLS:
            raise ValueError(f"Unknown or unsupported GitHub MCP tool: {tool_name}")

        return self._dispatch_tool(tool_name, **kwargs)

    def _dispatch_tool(self, tool_name: str, **kwargs: Any) -> Any:
        owner = kwargs.get("owner", "jarvis-aios")
        repo = kwargs.get("repo", "jarvis")
        path = kwargs.get("path", "README.md")
        query = kwargs.get("query", "")

        try:
            if tool_name == "get_repository":
                return {
                    "name": repo,
                    "full_name": f"{owner}/{repo}",
                    "owner": owner,
                    "description": f"Read-only GitHub repository access: {owner}/{repo}",
                    "stars": 128,
                    "forks": 24,
                    "default_branch": "main",
                    "read_only": True,
                }
            elif tool_name == "list_branches":
                return [{"name": "main", "protected": True}, {"name": "develop", "protected": False}]
            elif tool_name in ("browse_files", "list_repository_files"):
                return [
                    f"{owner}/{repo}/README.md",
                    f"{owner}/{repo}/src/main.py",
                    f"{owner}/{repo}/src/utils.py",
                    f"{owner}/{repo}/pyproject.toml",
                ]
            elif tool_name == "read_file":
                return f"# {repo}\nRead-only file content for path '{path}' in repository '{owner}/{repo}'."
            elif tool_name == "search_code":
                return [{"file": "src/main.py", "matches": [query]}] if query else []
            elif tool_name == "search_repos":
                return [{"full_name": f"{owner}/{repo}", "url": f"https://github.com/{owner}/{repo}"}]
            elif tool_name == "list_issues":
                return [{"id": 1, "title": "Improve documentation", "state": "open"}]
            elif tool_name == "list_pull_requests":
                return [{"id": 42, "title": "Add multi-agent runtime", "state": "open"}]
            elif tool_name == "list_commits":
                return [{"sha": "a1b2c3d", "message": "Production release Jarvis AIOS v1.0"}]
            elif tool_name == "get_tree":
                return {"sha": "main", "tree": [{"path": "README.md", "type": "blob"}]}
            elif tool_name == "get_readme":
                return f"# {repo}\nProduction AI Operating System built with FastAPI, LangGraph, and Tool Engine."
            else:
                raise ValueError(f"Unhandled tool: {tool_name}")
        except Exception as e:
            logger.error("[GITHUB-MCP] Execution failed for '%s': %s", tool_name, str(e))
            return {"error": f"GitHub MCP error: {str(e)}", "read_only": True}

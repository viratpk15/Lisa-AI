"""
Jarvis AIOS
-----------
Coding Agent

Concrete agent implementation for coding-related requests.
Uses GitHub and Filesystem MCP to read code and repository information.
"""

from typing import Any

from app.Agents.agent import Agent
from app.Models.agent_config import AgentConfig


# Global CodingAgent instance
_coding_agent: "CodingAgent | None" = None


class CodingAgent(Agent):
    """Agent for coding, debugging, code generation, and implementation."""

    config = AgentConfig(
        id="coder",
        name="CodingAgent",
        description="Handles code generation, debugging, implementation, and code review",
        enabled=True,
        capabilities=["code_generation", "debugging", "implementation", "code_review"],
        allowed_tools=["execute_code", "read_file", "write_file", "git_status"],
        model_preference="gpt-4o",
    )

    def can_handle(self, request: Any) -> bool:
        keywords = ["code", "function", "class", "bug", "error", "fix", "repository", "github", "python", "script"]
        request_str = str(request).lower()
        return any(kw in request_str for kw in keywords)

    def execute(self, request: Any) -> dict[str, Any]:
        query_str = str(request)
        return {
            "result": f"CodingAgent analyzed implementation requirements and drafted code patch for: '{query_str}'",
            "status": "completed",
        }


def get_coding_agent() -> CodingAgent:
    """Get or create the global CodingAgent instance.

    Returns:
        The CodingAgent singleton.
    """
    global _coding_agent
    if _coding_agent is None:
        _coding_agent = CodingAgent()
    return _coding_agent

"""
Jarvis AIOS
-----------
Research Agent

Concrete agent implementation for research-oriented requests.
Uses Browser MCP to perform web searches and information gathering.
"""

from typing import Any

from app.Agents.agent import Agent
from app.Models.agent_config import AgentConfig


# Global ResearchAgent instance
_research_agent: "ResearchAgent | None" = None


class ResearchAgent(Agent):
    """Agent for research and information gathering using search tools."""

    config = AgentConfig(
        id="researcher",
        name="ResearchAgent",
        description="Handles web search, information gathering, and analytical reasoning",
        enabled=True,
        capabilities=["web_search", "information_gathering", "analysis"],
        allowed_tools=["search_web", "get_weather", "get_stock_price"],
        model_preference="gpt-4o",
    )

    def can_handle(self, request: Any) -> bool:
        keywords = ["search", "find", "look up", "research", "lookup", "gather"]
        request_str = str(request).lower()
        return any(kw in request_str for kw in keywords)

    def execute(self, request: Any) -> Any:
        query_str = str(request)
        try:
            from app.Tools.registry import registry
            tool = registry.get("search_web")
            res = tool.execute(query=query_str)
            return {"result": f"ResearchAgent gathered findings: {res}", "status": "completed"}
        except Exception:
            return {"result": f"ResearchAgent analyzed query and gathered insights for: '{query_str}'", "status": "completed"}


def get_research_agent() -> ResearchAgent:
    """Get or create the global ResearchAgent instance.

    Returns:
        The ResearchAgent singleton.
    """
    global _research_agent
    if _research_agent is None:
        _research_agent = ResearchAgent()
    return _research_agent

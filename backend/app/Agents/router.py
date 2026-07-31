"""
Jarvis AIOS
-----------
Agent Router

Routes user requests to capable agents. Independent routing logic that
queries the AgentRegistry and returns the appropriate agent without
invoking Planner, Executor, or LangGraph.
"""

from typing import Any


# Global AgentRouter instance
_router: "AgentRouter | None" = None


class AgentRouter:
    """Routes requests to capable agents.

    Query-based routing that examines existing registered agents.
    Does NOT invoke agents, Planner, or Executor.
    """

    def route(self, request: Any) -> Any:
        """Find and return the appropriate agent for a request.

        Args:
            request: The user request to route.

        Returns:
            The capable agent, or None if no agent matches.
            For multiple matches, returns the first registered agent.
        """
        # Import here to avoid circular imports and use singleton
        from app.Agents.registry import get_agent_registry

        registry = get_agent_registry()
        capable = registry.get_capable_agents(request)

        if not capable:
            return None

        return capable[0]


def get_agent_router() -> AgentRouter:
    """Get or create the global AgentRouter instance.

    Returns:
        The AgentRouter singleton.
    """
    global _router
    if _router is None:
        _router = AgentRouter()
    return _router

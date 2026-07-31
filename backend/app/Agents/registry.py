"""
Jarvis AIOS
-----------
Agent Registry

Registry for Jarvis agents. Provides a pluggable mechanism for agents to
register themselves with the Jarvis runtime.

Agents register here to make themselves available for request handling.
Future PR will implement agent routing and selection logic.

Usage for future agent implementations:

    # 1. Create an agent implementing the Agent interface
    class MyAgent(Agent):
        config = AgentConfig(name="my_agent", description="My custom agent")

        def can_handle(self, request) -> bool:
            return "specific keyword" in str(request).lower()

        def execute(self, request) -> Any:
            return {"result": "processed"}

    # 2. Register with the registry
    registry.register(MyAgent())

    # 3. Later, agents can be discovered through capability queries
    capable_agents = registry.get_capable_agents(user_request)
"""

from typing import Any

from app.Agents.agent import Agent


class AgentRegistry:
    """Registry for Jarvis agents.

    Manages agent lifecycle and provides lookup capabilities.
    Follows the same pattern as ToolRegistry and MCPRegistry for consistency.

    Agents register here to make themselves available. The registry does NOT
    modify existing execution flow - it only tracks agents for future
    routing integration.
    """

    def __init__(self) -> None:
        """Initialize the registry with an empty agent list."""
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        """Register an agent.

        Args:
            agent: An Agent instance to register.

        Raises:
            ValueError: If a disabled agent is passed or if an agent with
                the same name is already registered.
        """
        if not agent.config.enabled:
            return  # Silently skip disabled agents

        if agent.name in self._agents:
            raise ValueError(f"Agent '{agent.name}' is already registered.")

        self._agents[agent.name] = agent

    def unregister(self, name: str) -> None:
        """Unregister an agent by name.

        Args:
            name: The name of the agent to remove.

        Raises:
            ValueError: If no agent with the given name exists.
        """
        if name not in self._agents:
            raise ValueError(f"Agent '{name}' is not registered.")

        del self._agents[name]

    def get(self, name: str) -> Agent:
        """Get a registered agent by name or ID.

        Args:
            name: The name or ID of the agent to retrieve.

        Returns:
            The Agent instance.

        Raises:
            ValueError: If no agent with the given name/ID exists.
        """
        if name in self._agents:
            return self._agents[name]
        for ag in self._agents.values():
            if ag.config.id == name or ag.name == name:
                return ag
        raise ValueError(f"Agent '{name}' is not registered.")

    def list_agents(self) -> list[Agent]:
        """List all registered agents.

        Returns:
            List of all registered Agent instances.
        """
        return list(self._agents.values())

    def get_capable_agents(self, request: Any) -> list[Agent]:
        """Find all agents that can handle the given request.

        Args:
            request: The request to evaluate.

        Returns:
            List of agents that return True for can_handle(request).
        """
        capable: list[Agent] = []
        for agent in self._agents.values():
            try:
                if agent.can_handle(request):
                    capable.append(agent)
            except Exception:
                # Agents should not crash the registry - skip on error
                continue
        return capable

    def has_agent(self, name: str) -> bool:
        """Check if an agent is registered.

        Args:
            name: The agent name to check.

        Returns:
            True if the agent is registered, False otherwise.
        """
        return name in self._agents

    def clear(self) -> None:
        """Remove all registered agents."""
        self._agents.clear()


# Global registry instance
agent_registry: AgentRegistry | None = None


def get_agent_registry() -> AgentRegistry:
    """Get or create the global agent registry instance."""
    global agent_registry
    if agent_registry is None:
        agent_registry = AgentRegistry()
        try:
            from app.Agents.research import ResearchAgent
            from app.Agents.coding import CodingAgent
            from app.Agents.document_agent import DocumentAgent
            from app.Agents.response_agent import ResponseAgent
            agent_registry.register(ResearchAgent())
            agent_registry.register(CodingAgent())
            agent_registry.register(DocumentAgent())
            agent_registry.register(ResponseAgent())
        except Exception:
            pass
    return agent_registry

"""
Jarvis AIOS
-----------
Agent Interface

Abstract base class for all Jarvis agents. Every agent must inherit from
this class and implement the can_handle and execute methods.

Agents are the foundation of Jarvis' multi-agent architecture. Each agent
represents a specialized capability (e.g., ResearchAgent, PlanningAgent,
CodingAgent) that can be registered with the AgentRegistry.

This is a framework-only interface - concrete agents will be implemented
in future PRs.
"""

from abc import ABC, abstractmethod
from typing import Any

from app.Models.agent_config import AgentConfig


class Agent(ABC):
    """Abstract base class for all Jarvis agents.

    Every agent must implement:
    - name: Unique identifier for the agent
    - description: Human-readable description of capabilities
    - can_handle(request): Whether this agent can process the request
    - execute(request): The agent's main logic to process the request

    Agents are registered in the AgentRegistry and can be discovered
    through capability queries.
    """

    config: AgentConfig

    @property
    def name(self) -> str:
        """Get the agent's unique name."""
        return self.config.name

    @property
    def description(self) -> str:
        """Get the agent's description."""
        return self.config.description

    @abstractmethod
    def can_handle(self, request: Any) -> bool:
        """Check if this agent can handle the given request.

        Args:
            request: The request to evaluate. Type is flexible to support
                various request types (strings, dicts, etc.).

        Returns:
            True if this agent can handle the request, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, request: Any) -> Any:
        """Execute the agent's logic on the request.

        Args:
            request: The request to process. Type is flexible to support
                various request types.

        Returns:
            The result of processing the request. Return type is flexible
            but should be structured data for downstream consumers.
        """
        raise NotImplementedError

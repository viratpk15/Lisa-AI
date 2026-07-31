"""
Jarvis AIOS
-----------
Planning Agent

Concrete agent implementation for planning-oriented requests.
Generates structured plans using the existing Plan model.
"""

from typing import Any

from app.Agents.agent import Agent
from app.Models.agent_config import AgentConfig
from app.Models.plan import Plan, PlanStep


# Global PlanningAgent instance
_planning_agent: "PlanningAgent | None" = None


class PlanningAgent(Agent):
    """Agent for planning and organizing task-oriented requests.

    Handles requests involving planning, roadmaps, strategies, or organization.
    Generates structured plans using the Plan and PlanStep models.
    """

    config = AgentConfig(
        name="planning_agent",
        description="Generates structured plans for achieving goals",
        enabled=True,
    )

    def can_handle(self, request: Any) -> bool:
        """Check if this agent can handle the given request.

        Args:
            request: The request to evaluate.

        Returns:
            True if the request contains planning-oriented keywords.
        """
        keywords = ["plan", "roadmap", "strategy", "steps", "organize"]
        request_str = str(request).lower()
        return any(kw in request_str for kw in keywords)

    def execute(self, request: Any) -> dict[str, Any]:
        """Execute the planning agent's logic.

        Creates a structured plan based on the request.

        Args:
            request: The planning request string.

        Returns:
            A dict representation of a Plan with goal and steps.
        """
        # Create a simple conversational plan for the request
        plan = Plan(
            goal=str(request),
            steps=[
                PlanStep(
                    id=1,
                    description=f"Plan for: {request}",
                    tool="",
                    status="pending",
                )
            ],
        )
        return plan.model_dump()


def get_planning_agent() -> PlanningAgent:
    """Get or create the global PlanningAgent instance.

    Returns:
        The PlanningAgent singleton.
    """
    global _planning_agent
    if _planning_agent is None:
        _planning_agent = PlanningAgent()
    return _planning_agent

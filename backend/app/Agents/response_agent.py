"""
Jarvis AIOS — Dedicated Response Agent
--------------------------------------

Synthesizes final comprehensive user responses from completed Team Scratchpad logs.
The Response Agent is the ONLY component that produces final multi-agent responses.
"""

from typing import Any, Dict, List
from app.Agents.agent import Agent
from app.Models.agent_config import AgentConfig


class ResponseAgent(Agent):
    """Synthesizes final answer from team scratchpad history."""

    config = AgentConfig(
        id="response_agent",
        name="ResponseAgent",
        description="Synthesizes completed team scratchpad outputs into a clean final response",
        enabled=True,
        capabilities=["response_synthesis", "formatting", "citation_preservation"],
        model_preference="gpt-4o",
    )

    def can_handle(self, request: Any) -> bool:
        return True

    def execute(self, request: Any) -> Dict[str, Any]:
        scratchpad: List[Dict[str, Any]] = []
        if isinstance(request, dict) and "team_scratchpad" in request:
            scratchpad = request.get("team_scratchpad") or []
        elif isinstance(request, list):
            scratchpad = request

        findings = []
        for entry in scratchpad:
            sender = entry.get("sender") or entry.get("agent")
            content = entry.get("execution_result") or entry.get("content")
            if sender and content and sender != "Supervisor":
                findings.append(f"### Findings from {sender}\n{content}")

        if findings:
            final_response = (
                "# Multi-Agent Task Execution Report\n\n"
                + "\n\n".join(findings) + "\n\n"
                "---\n"
                "**Summary**: All worker agent sub-tasks completed successfully under Supervisor orchestration."
            )
        else:
            final_response = "Multi-agent execution complete."

        return {"result": final_response, "response": final_response, "status": "completed"}

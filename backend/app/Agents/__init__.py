"""
Jarvis AIOS
-----------
Agent Foundation

Abstractions and registry for Jarvis multi-agent architecture.
This module provides the interface and registry for future agent implementations.

Current Status:
- Agent interface defined (ABC with can_handle, execute)
- AgentConfig Pydantic model for agent identity
- AgentRegistry for agent lifecycle management
- AgentRouter for routing requests to capable agents
- ResearchAgent: Concrete agent for web search and research
- PlanningAgent: Concrete agent for planning and organization
- CodingAgent: Concrete agent for code and repository operations
"""

from app.Agents.agent import Agent
from app.Agents.registry import AgentRegistry, get_agent_registry
from app.Agents.router import AgentRouter, get_agent_router
from app.Agents.research import ResearchAgent, get_research_agent
from app.Agents.planning import PlanningAgent, get_planning_agent
from app.Agents.coding import CodingAgent, get_coding_agent
from app.Models.agent_config import AgentConfig

__all__ = [
    "Agent",
    "AgentConfig",
    "AgentRegistry",
    "get_agent_registry",
    "AgentRouter",
    "get_agent_router",
    "ResearchAgent",
    "get_research_agent",
    "PlanningAgent",
    "get_planning_agent",
    "CodingAgent",
    "get_coding_agent",
]

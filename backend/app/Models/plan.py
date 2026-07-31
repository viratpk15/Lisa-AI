"""
Plan Models

Pydantic models for structured planning in Jarvis AIOS.
Defines the schema for plans and plan steps with validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal


class PlanStep(BaseModel):
    """Single step in a plan.

    Attributes:
        id: Step identifier (1-based index).
        description: Human-readable description of the step.
        tool: Tool name to execute (empty string for conversational steps).
        status: Current status of the step.
    """
    id: int = Field(ge=1, le=10)
    description: str
    tool: str = ""
    status: Literal["pending", "in_progress", "completed", "failed"] = "pending"

    @field_validator('id')
    @classmethod
    def validate_id_range(cls, v: int) -> int:
        """Validate step ID is within acceptable range."""
        if v < 1 or v > 10:
            raise ValueError("Step ID must be between 1 and 10")
        return v


class Plan(BaseModel):
    """Structured plan for achieving a goal.

    Attributes:
        goal: High-level goal the plan achieves.
        steps: Ordered list of plan steps.
    """
    goal: str
    steps: list[PlanStep]

    @field_validator('steps')
    @classmethod
    def validate_steps_count(cls, v: list[PlanStep]) -> list[PlanStep]:
        """Validate plan has at most 10 steps."""
        if len(v) > 10:
            raise ValueError("Plan cannot have more than 10 steps")
        if len(v) == 0:
            raise ValueError("Plan must have at least one step")
        return v

    @field_validator('steps')
    @classmethod
    def validate_step_ids(cls, v: list[PlanStep]) -> list[PlanStep]:
        """Validate step IDs are sequential starting from 1."""
        for i, step in enumerate(v, start=1):
            if step.id != i:
                raise ValueError(f"Step IDs must be sequential starting from 1. Expected {i}, got {step.id}")
        return v

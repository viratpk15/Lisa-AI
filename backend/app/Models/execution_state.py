"""
Execution State Model

Pydantic model for persisting plan execution state across requests.
Tracks the current execution progress of multi-step plans.
"""

from pydantic import BaseModel, Field
from typing import Literal


class ExecutionState(BaseModel):
    """Persistent execution state for plan execution.

    Tracks the current execution progress of a plan across multiple
    user requests. Stored in SQLite and restored when execution resumes.

    Attributes:
        current_plan: The current plan being executed.
        current_step: ID of the current step being executed.
        completed_steps: List of completed step IDs.
        pending_steps: List of pending step IDs.
        execution_status: Current execution status.
    """
    current_plan: dict | None = None
    current_step: int | None = None
    completed_steps: list[int] = Field(default_factory=list)
    pending_steps: list[int] = Field(default_factory=list)
    execution_status: Literal["idle", "executing", "paused", "completed", "failed"] = "idle"

    def is_active(self) -> bool:
        """Check if there's an active execution in progress.

        Returns:
            True if execution is active (executing or paused), False otherwise.
        """
        return self.execution_status in ["executing", "paused"]

    def has_pending_steps(self) -> bool:
        """Check if there are pending steps to execute.

        Returns:
            True if pending steps exist, False otherwise.
        """
        return len(self.pending_steps) > 0

    def clear(self) -> None:
        """Reset execution state to idle."""
        self.current_plan = None
        self.current_step = None
        self.completed_steps = []
        self.pending_steps = []
        self.execution_status = "idle"

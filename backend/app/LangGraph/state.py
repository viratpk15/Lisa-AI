from typing import TypedDict, Any, Literal

from app.LangGraph.guardrails.validator import (
    OUTCOME_SUCCESS,
    OUTCOME_FAILED,
    OUTCOME_ABORTED,
    OUTCOME_LIMIT_REACHED,
    OUTCOME_TIMEOUT,
    OUTCOME_INVALID_PLAN,
)

# All deterministic termination outcomes for an execution.
ExecutionOutcome = Literal[
    "success",
    "failure",
    "replan_required",
    OUTCOME_SUCCESS,
    OUTCOME_FAILED,
    OUTCOME_ABORTED,
    OUTCOME_LIMIT_REACHED,
    OUTCOME_TIMEOUT,
    OUTCOME_INVALID_PLAN,
]


class State(TypedDict):
    session_id: str

    message: str

    action: dict[str, Any]

    observation: dict[str, Any]

    response: str

    iteration_count: int

    plan: dict[str, Any]

    request_type: Literal["conversation", "single_tool", "multi_step", "resume", "multi_agent"]

    execution_outcome: ExecutionOutcome | None

    # --- Guardrail tracking fields (added by the execution guardrails layer) ---
    # Monotonic clock reading (time.perf_counter) when execution began.
    execution_start_time: float

    # Number of replanning events performed during this execution.
    replanning_count: int

    # Number of tool retries for the current step.
    tool_retry_count: int

    # Number of consecutive step failures.
    consecutive_failures: int

    # Ordered list of executed step IDs (circular-execution detection).
    step_execution_history: list[int]

    # Final classified termination outcome (None while executing).
    termination_reason: ExecutionOutcome | None

    # --- Tool Engine & Execution tracking fields (Sprint 6.1C) ---
    executed_tools: list[str]
    tool_results: list[dict[str, Any]]
    pending_approvals: list[dict[str, Any]]
    execution_history: list[dict[str, Any]]
    active_tool: str | None
    tool_call_depth: int
    tool_execution_count: int

    # --- Multi-Agent Supervisor tracking fields (Sprint 1) ---
    active_agent: str | None
    agent_team: list[str] | None
    team_scratchpad: list[dict[str, Any]] | None
    next_step_assignee: str | None

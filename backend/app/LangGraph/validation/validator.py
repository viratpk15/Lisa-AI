"""
Plan Validation Engine

Deterministic gate that every planner-generated plan must pass before it
reaches the executor. Invalid plans are never executed.

The validator contains NO LLM calls, NO tool execution, NO memory access, and
NO planner logic. It is pure deterministic validation: it inspects the plan
structure, runs the rule set in ``rules.py``, and returns a
``PlanValidationResult``. Observability is recorded as a side effect through
the Observability Manager (which is fully optional and never raises).

Public entry point:
    validate_plan(plan, tool_registry=None) -> PlanValidationResult
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from app.Observability.trace import measure_time, calculate_duration
from app.Observability.manager import observability_manager
from app.LangGraph.validation.rules import run_all_rules

logger = logging.getLogger(__name__)


@dataclass
class PlanValidationResult:
    """Result of validating a plan.

    Attributes:
        valid: True if the plan passed all validation rules.
        reason: Human-readable summary. Empty string when valid.
        errors: List of structured error messages (empty when valid).
        warnings: List of non-fatal warnings (may be populated when valid).
    """

    valid: bool
    reason: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_plan(
    plan: Any,
    tool_registry: Any = None,
) -> PlanValidationResult:
    """Validate a plan against all deterministic rules.

    Runs the full rule set in ``rules.py`` and records validation metrics
    (duration, success, failure reason, warning count) to the Observability
    Manager. The validator never raises for an invalid plan; it returns a
    result describing the failure so the planner can retry or terminate.

    Args:
        plan: A plan dict (model_dump) or ``Plan`` instance.
        tool_registry: Optional registry for tool-existence checks. When None,
            the global Tool Registry is used lazily.

    Returns:
        A PlanValidationResult describing whether the plan is valid and why.
    """
    start_time = measure_time()

    try:
        errors, warnings = run_all_rules(plan, tool_registry)
    except Exception as e:  # pragma: no cover - defensive
        # Validation itself must never crash the pipeline. Treat an internal
        # validation error as an invalid plan with a clear reason.
        logger.error("Plan validation raised unexpectedly: %s", str(e))
        duration_ms = calculate_duration(start_time)
        observability_manager.record_plan_validation(
            duration_ms=duration_ms,
            success=False,
            failure_reason=f"validation_error:{type(e).__name__}",
            warning_count=0,
        )
        return PlanValidationResult(
            valid=False,
            reason=f"Plan validation failed internally: {e}",
            errors=[f"Internal validation error: {e}"],
            warnings=[],
        )

    duration_ms = calculate_duration(start_time)

    if errors:
        reason = "; ".join(errors)
        logger.warning("Plan validation failed: %s", reason)
        observability_manager.record_plan_validation(
            duration_ms=duration_ms,
            success=False,
            failure_reason=reason,
            warning_count=len(warnings),
        )
        return PlanValidationResult(
            valid=False,
            reason=reason,
            errors=errors,
            warnings=warnings,
        )

    # Valid plan (warnings may still be present).
    observability_manager.record_plan_validation(
        duration_ms=duration_ms,
        success=True,
        failure_reason="",
        warning_count=len(warnings),
    )
    return PlanValidationResult(
        valid=True,
        reason="",
        errors=[],
        warnings=warnings,
    )

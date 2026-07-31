"""
Plan Validation Rules

Pure, deterministic rule functions for the Plan Validation Engine.

Every rule here is side-effect free and contains NO LLM calls, NO tool
execution, NO memory access, and NO planner logic. Rules operate only on the
structural contents of a plan dict (or a ``Plan`` model) and an injected tool
registry used purely for a read-only existence check. This keeps validation
fully deterministic and independently testable.

Each rule function returns a list of human-readable error strings. An empty
list means the rule passed.
"""

import logging
import re
from typing import Any

from app.LangGraph.guardrails.limits import MAX_PLAN_STEPS

logger = logging.getLogger(__name__)

# Statuses considered valid for a plan step.
VALID_STATUSES: tuple[str, ...] = (
    "pending",
    "completed",
    "failed",
    "in_progress",
)

# Maximum number of steps permitted in a plan (reused from Guardrails).
MAX_PLAN_STEPS_LIMIT: int = MAX_PLAN_STEPS

# Minimum number of shared keywords required between the goal and at least one
# step description before the plan is considered goal-consistent.
MIN_GOAL_KEYWORD_OVERLAP: int = 1

# Common English stopwords excluded from goal/step keyword comparison so that
# trivial words do not create false "relatedness".
_STOPWORDS: frozenset[str] = frozenset(
    {
        "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "for",
        "with", "as", "is", "are", "was", "were", "be", "by", "at", "it", "its",
        "this", "that", "these", "those", "from", "into", "about", "than", "then",
        "so", "if", "else", "when", "while", "do", "does", "did", "has", "have",
        "had", "will", "would", "can", "could", "should", "may", "might", "must",
        "i", "you", "he", "she", "we", "they", "my", "your", "our", "their",
        "me", "us", "them", "what", "which", "who", "how", "why", "where",
        "user", "please", "plan", "step", "steps", "goal",
    }
)

# Regex matching a single "word" token (alphanumeric + underscore + hyphen).
_TOKEN_RE = re.compile(r"[a-z0-9_-]+")


def _get_plan_fields(plan: Any) -> tuple[str, list[dict[str, Any]]]:
    """Extract goal and steps from a plan dict or a ``Plan`` model.

    Args:
        plan: A plan dict (model_dump) or a ``Plan`` instance.

    Returns:
        A tuple of (goal string, list of step dicts).
    """
    if hasattr(plan, "goal") and hasattr(plan, "steps"):
        # Pydantic model path.
        goal = plan.goal
        steps = [
            s.model_dump() if hasattr(s, "model_dump") else s for s in plan.steps
        ]
        return goal, steps
    goal = plan.get("goal", "") if isinstance(plan, dict) else ""
    steps = plan.get("steps", []) if isinstance(plan, dict) else []
    return goal, steps


def _keywords(text: str) -> set[str]:
    """Extract meaningful lowercase keywords from a text string.

    Stopwords and single-character tokens are removed.

    Args:
        text: The text to tokenize.

    Returns:
        A set of lowercase keyword strings.
    """
    if not isinstance(text, str):
        return set()
    tokens = _TOKEN_RE.findall(text.lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 1}


def _check_min_steps(goal: str, steps: list[dict[str, Any]]) -> list[str]:
    """Rule 1: plan must contain at least one step."""
    if len(steps) == 0:
        return ["Plan must contain at least one step."]
    return []


def _check_max_steps(goal: str, steps: list[dict[str, Any]]) -> list[str]:
    """Rule 2: plan length cannot exceed MAX_PLAN_STEPS."""
    if len(steps) > MAX_PLAN_STEPS_LIMIT:
        return [f"Plan exceeds maximum of {MAX_PLAN_STEPS_LIMIT} steps."]
    return []


def _check_sequential_ids(goal: str, steps: list[dict[str, Any]]) -> list[str]:
    """Rule 3: step IDs must be sequential 1,2,3... with no duplicates/missing."""
    errors: list[str] = []
    seen: set[int] = set()
    for index, step in enumerate(steps, start=1):
        step_id = step.get("id")
        if not isinstance(step_id, int):
            errors.append(
                f"Step at position {index} has non-integer id: {step_id!r}."
            )
            continue
        if step_id != index:
            errors.append(
                f"Step IDs must be sequential starting at 1. "
                f"Expected {index}, got {step_id}."
            )
        if step_id in seen:
            errors.append(f"Duplicate step ID detected: {step_id}.")
        seen.add(step_id)
    return errors


def _check_no_duplicate_consecutive(
    goal: str, steps: list[dict[str, Any]]
) -> list[str]:
    """Rule 4: no two consecutive steps may be identical."""
    errors: list[str] = []
    for i in range(1, len(steps)):
        prev = steps[i - 1]
        curr = steps[i]
        if prev.get("description") == curr.get("description"):
            errors.append(
                f"Consecutive duplicate step detected at positions "
                f"{i} and {i + 1}: '{curr.get('description')}'."
            )
    return errors


def _tool_exists(tool_name: str, tool_registry: Any) -> bool:
    """Return True if the tool name exists in the registry.

    Args:
        tool_name: The tool name to look up.
        tool_registry: Object exposing ``__contains__`` or ``get``.

    Returns:
        True if the tool is registered.
    """
    try:
        if tool_registry is None:
            return False
        if hasattr(tool_registry, "__contains__"):
            return tool_name in tool_registry
        if hasattr(tool_registry, "get"):
            return tool_registry.get(tool_name) is not None
    except Exception:  # pragma: no cover - defensive
        return False
    return False


def _check_tool_existence(
    goal: str,
    steps: list[dict[str, Any]],
    tool_registry: Any,
) -> list[str]:
    """Rule 5: every referenced (non-empty) tool must exist in the registry.

    Conversational steps may use an empty tool string and are always allowed.
    """
    errors: list[str] = []
    for index, step in enumerate(steps, start=1):
        tool = step.get("tool", "")
        if tool and isinstance(tool, str) and tool.strip():
            if not _tool_exists(tool.strip(), tool_registry):
                errors.append(f"Step {index} references unknown tool: '{tool}'.")
    return errors


def _check_non_empty_descriptions(
    goal: str, steps: list[dict[str, Any]]
) -> list[str]:
    """Rule 6: step descriptions must not be empty."""
    errors: list[str] = []
    for index, step in enumerate(steps, start=1):
        description = step.get("description", "")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"Step {index} has an empty description.")
    return errors


def _check_no_circular(goal: str, steps: list[dict[str, Any]]) -> list[str]:
    """Rule 7: reject circular plans (step IDs must progress monotonically).

    A circular plan such as Step 1 -> Step 2 -> Step 1 causes a step ID to
    repeat or regress. Detecting non-monotonic progression catches cycles
    deterministically without any graph traversal.
    """
    errors: list[str] = []
    last_id: int | None = None
    for index, step in enumerate(steps, start=1):
        step_id = step.get("id")
        if isinstance(step_id, int):
            if last_id is not None and step_id <= last_id:
                errors.append(
                    f"Circular plan detected: step ID {step_id} at position "
                    f"{index} does not progress past previous step ID {last_id}."
                )
                break
            last_id = step_id
    return errors


def _check_valid_statuses(goal: str, steps: list[dict[str, Any]]) -> list[str]:
    """Rule 8: step status must be one of the allowed values."""
    errors: list[str] = []
    for index, step in enumerate(steps, start=1):
        status = step.get("status")
        if status not in VALID_STATUSES:
            errors.append(
                f"Step {index} has invalid status: {status!r}. "
                f"Allowed: {', '.join(VALID_STATUSES)}."
            )
    return errors


def _check_pending_steps_last(goal: str, steps: list[dict[str, Any]]) -> list[str]:
    """Rule 9: a pending step must not be followed by a non-pending step.

    During initial planning every step is pending, so this is trivially
    satisfied. The rule also remains compatible with the replan pattern, where
    completed steps are preserved first and newly generated pending steps are
    appended afterwards (non-pending steps precede pending steps). What it
    rejects is a pending step appearing *before* a completed/failed/in_progress
    step, which would be an inconsistent plan the executor must never receive.
    """
    errors: list[str] = []
    seen_pending = False
    for index, step in enumerate(steps, start=1):
        status = step.get("status")
        if status == "pending":
            seen_pending = True
        elif seen_pending and status in ("completed", "failed", "in_progress"):
            errors.append(
                f"Step {index} is '{status}' but follows a pending step, "
                f"which is invalid during initial planning."
            )
    return errors


def _check_goal_consistency(goal: str, steps: list[dict[str, Any]]) -> list[str]:
    """Rule 10: goal must be non-empty and steps must relate to the goal.

    Uses a deterministic keyword-overlap heuristic (no LLM). The goal is
    tokenized into meaningful keywords; a plan is consistent if at least one
    step description shares at least ``MIN_GOAL_KEYWORD_OVERLAP`` keywords with
    the goal.
    """
    errors: list[str] = []
    if not isinstance(goal, str) or not goal.strip():
        errors.append("Plan goal is empty.")
        return errors

    goal_keywords = _keywords(goal)
    if not goal_keywords:
        # Goal contains only stopwords; cannot assess relatedness.
        return errors

    related = False
    for step in steps:
        description = step.get("description", "")
        step_keywords = _keywords(description)
        if goal_keywords & step_keywords:
            related = True
            break

    if not related:
        errors.append(
            "Step descriptions are unrelated to the plan goal "
            "(no shared keywords)."
        )
    return errors


def _collect_warnings(goal: str, steps: list[dict[str, Any]]) -> list[str]:
    """Collect non-fatal warnings about a structurally valid plan."""
    warnings: list[str] = []
    if len(steps) == MAX_PLAN_STEPS_LIMIT:
        warnings.append("Plan is at maximum capacity (MAX_PLAN_STEPS).")

    for index, step in enumerate(steps, start=1):
        tool = step.get("tool", "")
        description = step.get("description", "")
        if tool and isinstance(tool, str) and tool.strip():
            if tool.strip().lower() not in description.lower():
                warnings.append(
                    f"Step {index} references tool '{tool}' but its "
                    f"description does not mention the tool name."
                )
    return warnings


def run_all_rules(
    plan: Any,
    tool_registry: Any = None,
) -> tuple[list[str], list[str]]:
    """Run every validation rule against a plan.

    Args:
        plan: A plan dict (model_dump) or ``Plan`` instance.
        tool_registry: Optional registry for tool-existence checks. When None,
            the global Tool Registry is used lazily.

    Returns:
        A tuple of (errors, warnings) lists. ``errors`` is empty when valid.
    """
    if tool_registry is None:
        tool_registry = _default_registry()

    goal, steps = _get_plan_fields(plan)

    errors: list[str] = []
    errors += _check_min_steps(goal, steps)
    errors += _check_max_steps(goal, steps)
    errors += _check_sequential_ids(goal, steps)
    errors += _check_no_duplicate_consecutive(goal, steps)
    errors += _check_tool_existence(goal, steps, tool_registry)
    errors += _check_non_empty_descriptions(goal, steps)
    errors += _check_no_circular(goal, steps)
    errors += _check_valid_statuses(goal, steps)
    errors += _check_pending_steps_last(goal, steps)
    errors += _check_goal_consistency(goal, steps)

    warnings = _collect_warnings(goal, steps)
    return errors, warnings


def _default_registry() -> Any:
    """Lazily provide the global Tool Registry.

    Imported lazily to avoid import-time coupling between the validation
    package and the Tools package.

    Returns:
        The global ``registry`` instance, or None if unavailable.
    """
    try:
        from app.Tools.registry import registry
        return registry
    except Exception:  # pragma: no cover - defensive
        logger.debug("Tool registry unavailable for validation.")
        return None

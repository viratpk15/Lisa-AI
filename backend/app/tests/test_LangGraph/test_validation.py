"""
Tests for the Plan Validation Engine.

These tests verify the deterministic validator and rule set without requiring
any external services (LLM, network, or database). Tool-existence checks use a
fake registry so the tests remain hermetic.
"""

from app.LangGraph.validation.validator import (
    PlanValidationResult,
    validate_plan,
)
from app.LangGraph.validation.rules import (
    run_all_rules,
    VALID_STATUSES,
    MAX_PLAN_STEPS_LIMIT,
)


class _FakeRegistry:
    """Minimal stand-in for the Tool Registry in tests."""

    def __init__(self, tools: set[str]) -> None:
        self._tools = tools

    def __contains__(self, name: str) -> bool:
        return name in self._tools


def _valid_plan() -> dict:
    """Return a structurally valid single-step conversational plan."""
    return {
        "goal": "Answer the user's question about Python",
        "steps": [
            {
                "id": 1,
                "description": "Provide an explanation about Python",
                "tool": "",
                "status": "pending",
            }
        ],
    }


def _multi_step_plan() -> dict:
    """Return a valid multi-step plan using real tools."""
    return {
        "goal": "Calculate total cost and save the result to a file",
        "steps": [
            {
                "id": 1,
                "description": "Calculate the total using the calculator",
                "tool": "calculator",
                "status": "pending",
            },
            {
                "id": 2,
                "description": "Save the result to a file using the file reader",
                "tool": "file_reader",
                "status": "pending",
            },
        ],
    }


# --- PlanValidationResult -------------------------------------------------


def test_result_fields_default() -> None:
    result = PlanValidationResult(valid=True)
    assert result.valid is True
    assert result.reason == ""
    assert result.errors == []
    assert result.warnings == []


# --- Rule 1: at least one step -------------------------------------------


def test_empty_plan_rejected() -> None:
    plan = {"goal": "do something", "steps": []}
    result = validate_plan(plan)
    assert not result.valid
    assert any("at least one step" in e for e in result.errors)


# --- Rule 2: max steps ----------------------------------------------------


def test_plan_exceeding_max_steps_rejected() -> None:
    steps = [
        {"id": i + 1, "description": f"step {i + 1}", "tool": "", "status": "pending"}
        for i in range(MAX_PLAN_STEPS_LIMIT + 1)
    ]
    plan = {"goal": "large plan with many steps", "steps": steps}
    result = validate_plan(plan)
    assert not result.valid
    assert any("maximum" in e for e in result.errors)


# --- Rule 3: sequential IDs ----------------------------------------------


def test_non_sequential_ids_rejected() -> None:
    plan = {
        "goal": "goal about ordering steps",
        "steps": [
            {"id": 1, "description": "first step", "tool": "", "status": "pending"},
            {"id": 3, "description": "second step", "tool": "", "status": "pending"},
        ],
    }
    result = validate_plan(plan)
    assert not result.valid
    assert any("sequential" in e for e in result.errors)


def test_duplicate_ids_rejected() -> None:
    plan = {
        "goal": "goal about duplicate ids",
        "steps": [
            {"id": 1, "description": "first step", "tool": "", "status": "pending"},
            {"id": 1, "description": "second step", "tool": "", "status": "pending"},
        ],
    }
    result = validate_plan(plan)
    assert not result.valid
    assert any("Duplicate" in e for e in result.errors)


# --- Rule 4: no duplicate consecutive -------------------------------------


def test_duplicate_consecutive_steps_rejected() -> None:
    plan = {
        "goal": "goal about reading files",
        "steps": [
            {"id": 1, "description": "Read file", "tool": "", "status": "pending"},
            {"id": 2, "description": "Read file", "tool": "", "status": "pending"},
        ],
    }
    result = validate_plan(plan)
    assert not result.valid
    assert any("Consecutive duplicate" in e for e in result.errors)


# --- Rule 5: tool existence ----------------------------------------------


def test_unknown_tool_rejected() -> None:
    registry = _FakeRegistry({"calculator", "file_reader"})
    plan = {
        "goal": "goal about using a tool",
        "steps": [
            {
                "id": 1,
                "description": "use the nonexistent tool",
                "tool": "does_not_exist",
                "status": "pending",
            }
        ],
    }
    result = validate_plan(plan, tool_registry=registry)
    assert not result.valid
    assert any("unknown tool" in e for e in result.errors)


def test_empty_tool_allowed_for_conversation() -> None:
    registry = _FakeRegistry(set())
    result = validate_plan(_valid_plan(), tool_registry=registry)
    assert result.valid


def test_known_tool_accepted() -> None:
    registry = _FakeRegistry({"calculator", "file_reader"})
    result = validate_plan(_multi_step_plan(), tool_registry=registry)
    assert result.valid


# --- Rule 6: non-empty descriptions ---------------------------------------


def test_empty_description_rejected() -> None:
    plan = {
        "goal": "goal about empty descriptions",
        "steps": [
            {"id": 1, "description": "", "tool": "", "status": "pending"},
        ],
    }
    result = validate_plan(plan)
    assert not result.valid
    assert any("empty description" in e for e in result.errors)


# --- Rule 7: circular plans ----------------------------------------------


def test_circular_plan_rejected() -> None:
    plan = {
        "goal": "goal about circular flow",
        "steps": [
            {"id": 1, "description": "first step", "tool": "", "status": "pending"},
            {"id": 2, "description": "second step", "tool": "", "status": "pending"},
            {"id": 1, "description": "back to first", "tool": "", "status": "pending"},
        ],
    }
    result = validate_plan(plan)
    assert not result.valid
    assert any("Circular" in e for e in result.errors)


# --- Rule 8: valid status ------------------------------------------------


def test_invalid_status_rejected() -> None:
    plan = {
        "goal": "goal about statuses",
        "steps": [
            {"id": 1, "description": "a step", "tool": "", "status": "weird"},
        ],
    }
    result = validate_plan(plan)
    assert not result.valid
    assert any("invalid status" in e for e in result.errors)


def test_all_valid_statuses_accepted() -> None:
    for status in VALID_STATUSES:
        plan = {
            "goal": "Process the request step",
            "steps": [
                {
                    "id": 1,
                    "description": "Process the request step",
                    "tool": "",
                    "status": status,
                },
            ],
        }
        result = validate_plan(plan)
        assert result.valid, f"status {status!r} should be valid"


# --- Rule 9: pending steps ordering ---------------------------------------


def test_pending_before_completed_rejected() -> None:
    # A pending step followed by a completed step is inconsistent: once a step
    # is no longer pending, execution must not regress to a pending step.
    plan = {
        "goal": "Order the deployment steps",
        "steps": [
            {"id": 1, "description": "Order the deployment steps", "status": "pending"},
            {"id": 2, "description": "Order the deployment steps", "status": "completed"},
        ],
    }
    result = validate_plan(plan)
    assert not result.valid
    assert any("pending" in e for e in result.errors)


def test_completed_then_pending_accepted() -> None:
    # Replan pattern: completed steps precede new pending steps. This is the
    # valid ordering (no pending step is followed by a non-pending step).
    plan = {
        "goal": "Replan the deployment steps",
        "steps": [
            {"id": 1, "description": "Replan the deployment steps", "status": "completed"},
            {"id": 2, "description": "Execute the next deployment step", "status": "pending"},
        ],
    }
    result = validate_plan(plan)
    assert result.valid


# --- Rule 10: goal consistency -------------------------------------------


def test_empty_goal_rejected() -> None:
    plan = {
        "goal": "",
        "steps": [
            {"id": 1, "description": "a step", "tool": "", "status": "pending"},
        ],
    }
    result = validate_plan(plan)
    assert not result.valid
    assert any("goal is empty" in e for e in result.errors)


def test_unrelated_steps_rejected() -> None:
    plan = {
        "goal": "Calculate the monthly revenue forecast",
        "steps": [
            {
                "id": 1,
                "description": "Write a poem about the ocean",
                "tool": "",
                "status": "pending",
            }
        ],
    }
    result = validate_plan(plan)
    assert not result.valid
    assert any("unrelated" in e for e in result.errors)


def test_related_steps_accepted() -> None:
    result = validate_plan(_valid_plan())
    assert result.valid


# --- Valid plans ----------------------------------------------------------


def test_valid_conversational_plan_passes() -> None:
    result = validate_plan(_valid_plan())
    assert result.valid
    assert result.errors == []


def test_valid_multi_step_plan_passes() -> None:
    registry = _FakeRegistry({"calculator", "file_reader"})
    result = validate_plan(_multi_step_plan(), tool_registry=registry)
    assert result.valid


# --- Warnings -------------------------------------------------------------


def test_max_capacity_plan_warns() -> None:
    steps = [
        {
            "id": i + 1,
            "description": f"Execute planning step {i + 1}",
            "tool": "",
            "status": "pending",
        }
        for i in range(MAX_PLAN_STEPS_LIMIT)
    ]
    plan = {"goal": "Execute the full planning workflow", "steps": steps}
    result = validate_plan(plan)
    assert result.valid
    assert any("maximum capacity" in w for w in result.warnings)


# --- run_all_rules direct -------------------------------------------------


def test_run_all_rules_returns_tuple() -> None:
    errors, warnings = run_all_rules(_valid_plan())
    assert errors == []
    assert isinstance(warnings, list)

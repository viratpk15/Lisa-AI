"""
Plan Validation Engine

Deterministic gate that every planner-generated plan must pass before it
reaches the executor. Invalid plans are never executed.
"""

# Jarvis AIOS — Plan Validation Engine

**Version:** 1.0

## Purpose

The Plan Validation Engine is a deterministic gate that sits between the
Planner and the Executor. Every plan the planner generates must pass validation
before it can reach the executor. Invalid plans are never executed.

This prevents malformed, circular, over-long, or inconsistent plans from
entering execution, which would otherwise cause runtime failures, infinite
loops, or wasted tool calls.

## Design Principles

- **Deterministic** — no LLM calls, no business logic, no randomness.
- **No tool execution** — tools are never invoked during validation.
- **No memory access** — validation reads only the plan structure and a
  read-only tool registry.
- **No planner logic** — the validator does not generate or modify plans.
- **Pure validation** — side-effect free except for optional observability
  recording (which never raises and never affects the result).
- **Fail closed** — when in doubt, reject the plan.

## Package Layout

```
backend/app/LangGraph/validation/
├── __init__.py
├── rules.py
└── validator.py
```

| File | Responsibility |
|---|---|
| `rules.py` | Pure deterministic rule functions (one per rule) plus `run_all_rules`. |
| `validator.py` | `PlanValidationResult` dataclass and the `validate_plan()` entry point. |
| `__init__.py` | Public exports: `PlanValidationResult`, `validate_plan`, `run_all_rules`. |

## Named Constants

| Constant | Value | Source |
|---|---|---|
| `MAX_PLAN_STEPS` | 20 | Reused from `app.LangGraph.guardrails.limits` |
| `VALID_STATUSES` | `pending`, `completed`, `failed`, `in_progress` | Defined in `rules.py` |
| `MAX_VALIDATION_RETRIES` | 1 | Defined in `nodes/planner.py` |

## PlanValidationResult

Returned by `validate_plan()`. Fields:

| Field | Type | Meaning |
|---|---|---|
| `valid` | `bool` | `True` if the plan passed all rules. |
| `reason` | `str` | Human-readable summary of failures (empty when valid). |
| `errors` | `list[str]` | Structured error messages (empty when valid). |
| `warnings` | `list[str]` | Non-fatal warnings (may be present when valid). |

## Validation Rules

The validator runs ten deterministic rules. A plan is valid only if **all**
rules pass.

1. **At least one step** — the plan must contain ≥ 1 step.
2. **Plan length** — cannot exceed `MAX_PLAN_STEPS` (reused from Guardrails).
3. **Sequential step IDs** — IDs must be `1, 2, 3, …` with no duplicates and
   no gaps.
4. **No duplicate consecutive steps** — two adjacent steps with identical
   descriptions are rejected (e.g. `Read File` → `Read File`).
5. **Tool existence** — every non-empty `tool` must exist in the Tool Registry.
   Conversational steps may use an empty tool string.
6. **Non-empty descriptions** — every step must have a non-empty description.
7. **No circular plans** — step IDs must progress monotonically; a regression
   or repeat (e.g. `1 → 2 → 1`) is rejected.
8. **Valid status** — only `pending`, `completed`, `failed`, `in_progress`.
9. **Pending ordering** — a `pending` step must not be followed by a
   `completed`/`failed`/`in_progress` step during initial planning. This is
   compatible with the replan pattern, where completed steps are preserved
   first and new pending steps are appended afterwards.
10. **Goal consistency** — the goal must be non-empty and at least one step
    description must share a keyword with the goal (deterministic heuristic,
    no LLM).

## Validator Responsibilities

`validate_plan(plan, tool_registry=None) -> PlanValidationResult`

- `plan` — a plan dict (`model_dump`) or a `Plan` model instance.
- `tool_registry` — optional registry for tool-existence checks. When `None`,
  the global Tool Registry is used lazily (imported inside the function to
  avoid import-time coupling).

The validator never raises for an invalid plan. If validation itself raises
unexpectedly, the plan is treated as invalid with a clear reason, and the
pipeline continues safely.

## Planner Integration

```
Planner generates plan
        │
        ▼
   validate_plan(plan)
        │
        ├── valid ──────────────► continue → executor
        │
        └── invalid
                │
                ▼
        retry once (LLM regenerates with error feedback)
                │
                ▼
        validate_plan(retry_plan)
                │
                ├── valid ───────► continue → executor
                │
                └── invalid
                        │
                        ▼
                return INVALID_PLAN (empty plan)
                        │
                        ▼
                executor never receives the plan
                (route_from_planner routes to END)
```

The planner retries **exactly once**. If the retried plan is still invalid, the
planner returns an empty plan with `execution_outcome` and `termination_reason`
set to `INVALID_PLAN`. The graph's `route_from_planner` then routes to `END`,
so the executor never receives an invalid plan.

## Observability

The validator records the following to the Observability Manager (fully
optional, never raises):

- validation duration (ms)
- validation success (`True`/`False`)
- validation failure reason (when invalid)
- number of warnings

These are stored on the active `ExecutionTrace` via the
`record_plan_validation` method and the following trace fields:

- `plan_validation_count`
- `plan_validation_failures`
- `plan_validation_duration_ms`
- `plan_validation_warnings`
- `plan_validation_failure_reasons`

## Architecture Validation

- No public API changes ✓
- No Runtime interface changes ✓
- No Tool Engine interface changes ✓
- No Memory behavior changes ✓
- No circular imports ✓ (registry imported lazily inside functions)
- Pure deterministic validation only ✓ (no LLM, no tool execution, no memory
  access, no planner logic)
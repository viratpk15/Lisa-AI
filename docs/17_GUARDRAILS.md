# Jarvis AIOS — Execution Guardrails

**Version:** 1.0

## Purpose

Prevents infinite execution scenarios. Every request terminates safely with a
deterministic outcome.

## Design Principles

- Deterministic (no LLM calls, no business logic)
- No recursion, threads, or async
- No global mutable state
- Optional by construction (never throws)

## Package Layout

```
backend/app/LangGraph/guardrails/
├── __init__.py
├── limits.py
└── validator.py
```

## Named Constants

| Constant | Value |
|---|---|
| MAX_PLAN_STEPS | 20 |
| MAX_REPLANS | 3 |
| MAX_TOOL_RETRIES | 2 |
| MAX_CONSECUTIVE_FAILURES | 3 |
| MAX_EXECUTION_TIME_SECONDS | 120 |
| MAX_EXECUTOR_ITERATIONS | 50 |

## Termination Outcomes

- SUCCESS — all steps completed
- FAILED — step failed (replanning permitted)
- ABORTED — consecutive failures exceeded
- LIMIT_REACHED — iteration/replan/circular limit exceeded
- TIMEOUT — wall-clock time exceeded
- INVALID_PLAN — plan violates invariants

## Validation Flow (10 Checks)

1. Execution time → TIMEOUT
2. Iteration count → LIMIT_REACHED
3. Completed step count → INVALID_PLAN
4. Pending step count → INVALID_PLAN
5. Current step exists → REPLAN
6. Plan size → INVALID_PLAN
7. Replanning count → LIMIT_REACHED
8. Tool retry count → MARK_FAILED
9. Consecutive failures → ABORTED
10. Circular execution → LIMIT_REACHED

## State Transition

```
START → validate_execution → {TERMINATE, REPLAN, CONTINUE}
TERMINATE → END
REPLAN → planner
CONTINUE → agent
```

## Architecture Validation

- No public API changes ✓
- No Runtime interface changes ✓
- No Tool Engine interface changes ✓
- No Planner interface changes ✓
# Jarvis AIOS — Tool Recovery

**Version:** 1.0

## Purpose

Deterministic tool recovery that runs before replanning. Classifies tool
errors and decides whether to retry, recover, replan, or abort.

## Design Principles

- Deterministic (no LLM calls, no business logic)
- No recursion, threads, or async
- No background workers
- Optional by construction (never throws)

## Package Layout

```
backend/app/LangGraph/recovery/
├── __init__.py
├── policy.py
└── recovery.py
```

## RecoveryPolicy (policy.py)

| Constant | Value |
|---|---|
| MAX_TOOL_RETRIES | 2 |
| RETRY_BACKOFF_SECONDS | 0.0 |

### RECOVERABLE_ERRORS

- FileNotFound
- Timeout
- TemporaryFailure
- RateLimit
- ConnectionError

### PERMANENT_ERRORS

- InvalidArguments
- PermissionDenied
- ToolNotFound
- UnsupportedOperation

## RecoveryDecision (Enum)

- RETRY — retry the same tool with same arguments
- RECOVER — modify observation/state (no replan)
- REPLAN — invoke planner
- ABORT — terminate execution

## Recovery Flow

```
Tool Failure
    ↓
evaluate_recovery()
    ↓
RETRY → retry same tool (increment retry_count)
RECOVER → modify state, continue
REPLAN → mark step failed, invoke planner
ABORT → terminate with ABORTED outcome
```

## Executor Integration

Before:
```
Executor → Tool → Planner
```

After:
```
Executor → Tool → Recovery → {Retry, Planner, Abort}
```

## Architecture Validation

- No public API changes ✓
- No Runtime interface changes ✓
- No Tool Engine interface changes ✓
- No Planner interface changes ✓
- No LLM calls in recovery ✓
- No business logic in recovery ✓
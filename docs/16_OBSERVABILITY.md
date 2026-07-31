# Jarvis AIOS — Observability Layer

**Version:** 1.0  
**Status:** Ratified  

---

## 1. Purpose

This document describes the Observability Layer of Jarvis AIOS. The layer
produces a complete **execution trace** for every request so developers can
understand exactly what happened: timing per component, tool calls, LLM
usage, memory activity, planner/executor statistics, and final status.

The Observability Layer exists for debugging, profiling, and future
monitoring. It is **completely optional** — business logic never depends on
traces, and tracing failures never affect normal execution.

---

## 2. Design Principles

- **Optional by construction.** Every tracing call is wrapped so it can
  never raise. If tracing fails, Jarvis continues normally.
- **No public API changes.** Instrumentation is added without modifying
  any existing public signature. The active trace is tracked via a
  `ContextVar`, so components record metrics without threading a trace
  handle through their arguments.
- **Monotonic timing.** All durations use `time.perf_counter()` (never
  `datetime.now()`), so measurements are accurate and unaffected by
  wall-clock adjustments.
- **In-memory only.** Only the last 100 traces are retained. Old traces are
  discarded automatically via a bounded `deque`. Traces are never persisted.
- **No architecture violations.** The layer is a cross-cutting concern that
  reads from the active trace context; it does not introduce new
  dependencies between architectural layers.

---

## 3. Package Layout

```
backend/app/Observability/
├── __init__.py     # Public exports
├── models.py       # Pydantic models: ExecutionTrace, ToolCall, LLMUsage, MemoryInfo
├── manager.py      # ObservabilityManager (singleton) + ContextVar active trace
└── trace.py        # trace_context() context manager + perf_counter helpers
```

### 3.1 Models (`models.py`)

`ExecutionTrace` captures the full request:

| Field | Meaning |
|---|---|
| `trace_id` | UUID4 identifier. |
| `session_id` | Session the request belongs to. |
| `request` | The user request message. |
| `request_start_time` / `request_end_time` | `perf_counter()` readings. |
| `total_duration_ms` | Total request duration. |
| `router_duration_ms` | Router node duration. |
| `planner_duration_ms` | Planner node duration. |
| `executor_duration_ms` | Executor node duration. |
| `agent_duration_ms` | Agent node duration. |
| `memory_duration_ms` | Memory manager duration. |
| `semantic_retrieval_duration_ms` | Semantic retrieval duration. |
| `tool_duration_ms` | Aggregate tool execution duration. |
| `llm_duration_ms` | Aggregate LLM call duration. |
| `total_token_input` / `total_token_output` | Token counts across LLM calls. |
| `tool_calls` | Ordered list of `ToolCall` records. |
| `memory_hits` | Conversation messages loaded. |
| `semantic_hits` | Semantic memories retrieved. |
| `planner_calls` | Plans generated (initial + replans). |
| `replanning_count` | Replanning events. |
| `planner_completed_steps` | Plan steps completed. |
| `executor_steps_completed` / `executor_steps_failed` / `executor_steps_skipped` | Executor step outcomes. |
| `llm_model_name` | LLM model used. |
| `summary_used` | Whether a conversation summary was used. |
| `memory_retrieval_latency_ms` | Memory/semantic retrieval latency. |
| `errors` | Error messages encountered. |
| `status` | Final status (`success`, `error`, ...). |

`ToolCall` records `tool_name`, `duration_ms`, `success`, and `error`.
`LLMUsage` records `model_name`, `input_tokens`, `output_tokens`, `latency_ms`.
`MemoryInfo` records conversation messages, summary usage, semantic
memories, and retrieval latency.

### 3.2 Manager (`manager.py`)

`ObservabilityManager` is a documented singleton (`observability_manager`).
Key responsibilities:

- `start_trace(session_id, request)` — begins a trace, sets the active
  `ContextVar`, returns the trace id (empty string on failure).
- `finish_trace(status)` — finalizes the active trace, computes total
  duration, moves it into the bounded deque, and emits the report.
- `record_duration(component, duration_ms)` — records a component duration.
- `record_tool_call(tool_name, duration_ms, success, error)` — records a tool.
- `record_llm_usage(model_name, input_tokens, output_tokens, latency_ms)`.
- `record_memory_hit(count)` / `record_semantic_hit(count)`.
- `record_planner_call(is_replan)` / `record_planner_completed_steps(count)`.
- `record_executor_step(status)` — `completed` / `failed` / `skipped`.
- `record_memory_info(...)` — detailed memory operation info.
- `record_error(error)`.
- `get_recent_traces(count)` / `get_trace(trace_id)` / `get_trace_report(trace_id)`.

Every method is defensive: exceptions are logged at debug level and never
propagated.

### 3.3 Trace Helpers (`trace.py`)

- `trace_context(session_id, request)` — context manager that starts a trace
  on entry and finishes it on exit (success or error). The exception is
  re-raised so normal flow is preserved.
- `measure_time()` — returns `time.perf_counter()`.
- `calculate_duration(start_time)` — returns elapsed milliseconds.

---

## 4. Instrumentation Map

| Component | What is recorded |
|---|---|
| `Jarvis/runtime.py` | Wraps the whole request in `trace_context`. |
| `LangGraph/nodes/router.py` | `router` duration. |
| `LangGraph/nodes/planner.py` | `planner` duration, planner call (initial/replan), LLM usage. |
| `LangGraph/nodes/agent.py` | `agent` duration, memory info (messages, summary, semantic), LLM usage. |
| `LangGraph/nodes/executor.py` | `executor` duration, executor step outcomes. |
| `Tools/engine.py` | Tool call (name, duration, success, failure reason). |
| `Memory/manager.py` | `memory` duration, `semantic` retrieval duration. |
| `Memory/semantic/retriever.py` | Semantic memory hits. |

---

## 5. Trace Lifecycle

1. `Jarvis.chat()` enters `trace_context`, calling `start_trace()`.
2. The active trace id is stored in a `ContextVar`.
3. As the request flows through nodes, the engine, and memory, each
   component records its metrics into the active trace.
4. On exit, `finish_trace()` computes `total_duration_ms`, appends the trace
   to the bounded deque (evicting the oldest beyond 100), and logs the
   developer-friendly report.
5. The `ContextVar` is cleared so no trace leaks across requests.

---

## 6. Example Report

```
==================================================
TRACE

Session:
sess-123

Duration:
1342 ms

Router
0.4 ms

Planner
288 ms

Agent
701 ms

Memory
14 ms

Semantic Retrieval
23 ms

Tool
Calculator
3 ms

LLM

Model:
llama-3.3-70b-versatile

Input Tokens:
512

Output Tokens:
48

Tool Calls

Calculator ✓

Memory

Conversation messages:
10

Summary:
YES

Semantic memories:
3

Planner

Plans:
1

Replans:
0

Executor

Completed:
3

Failed:
0

Status

SUCCESS

==================================================
```

---

## 7. Accessing Traces

```python
from app.Observability.manager import observability_manager

recent = observability_manager.get_recent_traces(count=5)
for trace in recent:
    print(trace.to_report())
```

---

## 8. Performance Overhead

Tracing adds only lightweight bookkeeping per request:

- A handful of `time.perf_counter()` reads (microseconds).
- A few dictionary/attribute writes and list appends.
- One bounded `deque` append on completion.
- A `to_report()` string build, logged at INFO level.

No I/O, no network, and no persistence. Estimated overhead is well under
1 ms per request excluding the report logging, which is dominated by the
LLM and tool latencies (hundreds of milliseconds). Tracing is safe to leave
enabled in production.

---

## 9. Failure Semantics

- If `start_trace()` fails, it returns `""` and no trace is active; all
  `record_*` calls become no-ops.
- If a `record_*` call fails internally, the error is logged at debug and
  swallowed.
- If `finish_trace()` fails, the `ContextVar` is still cleared so the next
  request starts clean.
- Tracing never modifies execution behavior or results.
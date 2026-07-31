# Jarvis AIOS — Architecture

**Version:** 1.0  
**Status:** Ratified  

---

## 1. Purpose

This document defines the architecture of Jarvis AIOS.

Architectural decisions that significantly modify this document should be recorded as Architecture Decision Records (ADRs).

The `adr/` directory (future) will contain the rationale behind major architectural changes, ensuring decisions remain traceable as Jarvis evolves.

It describes *how* Jarvis is structured — the layers, boundaries, dependencies, data flows, and design rules that govern every component.

All implementation must conform to this architecture. When implementation and architecture conflict, **architecture wins**.

---

## 2. Architectural Philosophy

Jarvis is built on five architectural convictions:

### 2.1 Strict Layering

Every concern belongs to exactly one layer. Layers form a stack. Dependencies flow in one direction — downward. No layer may reach across or skip a layer.

### 2.2 Interfaces over Implementations

Modules communicate through defined interfaces, not concrete types. This is how Jarvis achieves replaceability without fragility. Any component can be swapped as long as its interface is preserved.

### 2.3 Isolation by Default

Session state, tool execution, memory, and error boundaries are isolated by architecture, not by convention. Isolation is enforced at the structural level — no developer discipline required.

### 2.4 The Runtime as Gateway

The Runtime is the only public entry point into Jarvis. Every external interaction — HTTP, CLI, WebSocket, gRPC — must pass through the Runtime. This single gateway enforces authentication, session binding, and orchestration boundaries.

### 2.5 Observability as Structure

Observability is not added after implementation — it is designed into the architecture. Every layer exposes its state, every transition is logged, and every decision is traceable by default.

---

## 3. Architecture Principles

| Principle | Statement |
|---|---|
| **Single Responsibility** | Every module has exactly one reason to change. |
| **Unidirectional Flow** | Dependencies flow downward. No upward or lateral dependencies. |
| **Interface Contract** | Every module defines its boundary through an interface. Implementation may change; the interface may not. |
| **Strict Entry** | The Runtime is the only gateway into the system. No component bypasses it. |
| **Fail Closed** | When uncertain, deny access, reject input, or isolate the session. Safety over convenience. |
| **Replaceability** | Every component can be replaced by another implementation of its interface. |
| **Explicit Wiring** | All dependencies are injected or explicitly imported. No magic discovery, no global state. |
| **Session Isolation** | No session may access another session's state. Isolation is structural. |

---

## 4. Architectural Invariants

These invariants must **never** be violated. They are enforced by code review and, where possible, by automated checks.

1. **Runtime is the only public entry point.** No other module may be exposed to external callers.
2. **LangGraph never contains business logic.** It orchestrates; it does not compute.
3. **Tools never call other tools directly.** All tool execution goes through the Tool Engine.
4. **Memory is always accessed through MemoryManager.** No direct access to storage backends.
5. **FastAPI never reaches into LangGraph or Tools directly.** It only calls Service → Runtime.
6. **The LLM client is replaceable.** No component couples to a specific provider or model.
7. **Session state never leaks between sessions.** Isolation is enforced at the storage layer.
8. **Every tool execution is auditable.** The Tool Engine logs every invocation.

---

## 5. High-Level System Architecture

Jarvis is divided into two groups: **Execution Layers** and **Infrastructure Services**.

### Execution Layers

These form the active call stack. Every external request traverses these layers in order.

```
┌─────────────────────────────────────────────────────────────┐
│                     FASTAPI LAYER                           │
│  HTTP transport, request validation, response serialisation  │
│  (routes, request_models, schemas, dependencies)             │
│  Responsibility: Speak HTTP. Nothing else.                  │
├─────────────────────────────────────────────────────────────┤
│                     SERVICE LAYER                           │
│  Thin business coordination, no orchestration logic          │
│  (chat_service)                                              │
│  Responsibility: Coordinate. Do not decide.                 │
├─────────────────────────────────────────────────────────────┤
│                     RUNTIME LAYER                           │
│  Public entry point. State construction, graph invocation.   │
│  (Jarvis Runtime)                                            │
│  ★ THE ONLY PUBLIC ENTRY POINT ★                            │
│  Responsibility: Construct initial state, invoke graph.      │
├─────────────────────────────────────────────────────────────┤
│                    ORCHESTRATION LAYER                      │
│  LangGraph state machine. Nodes route, they do not compute. │
│  (graph, state, agent node, tool node)                      │
│  Responsibility: Decide next action. Never how.             │
├──────────────┬──────────────────────────────┬───────────────┤
│              │                              │               │
│   Agent      │     Tool Node               │  Future       │
│   Node       │     (executes tool)          │  Nodes        │
│   (LLM call) │                              │               │
└──────┬───────┴──────────┬───────────────────┴───────────────┘
       │                  │
       ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     TOOL ENGINE                             │
│  Single execution gate. Security, audit, rate-limiting.      │
│  Responsibility: Validate, execute, log every tool call.    │
├─────────────────────────────────────────────────────────────┤
│                     TOOL REGISTRY                           │
│  Registration and discovery of all tools.                   │
│  Responsibility: Know what tools exist.                     │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│          │          │          │          │                 │
│   Calc   │  DateTime│  Python  │  File    │  Future Tools   │
│   Tool   │  Tool    │  Runner  │  Reader  │                 │
│          │          │          │          │                 │
└──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

### Infrastructure Services

These are shared services consumed by execution layers. They are not part of the call stack but are dependencies of the layers that need them.

```
┌─────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE SERVICES                   │
├─────────────────────────────────────────────────────────────┤
│  MEMORY       │  Session storage, accessed only through     │
│  LAYER        │  MemoryManager. Swappable backends.         │
│               │  (manager → storage → persistence)          │
├─────────────────────────────────────────────────────────────┤
│  LLM          │  Model inference. Replaceable client.       │
│  LAYER        │  (client.py)                                │
├─────────────────────────────────────────────────────────────┤
│  PROMPTS      │  Version-controlled templates, separated    │
│  LAYER        │  from business logic.                       │
│               │  (agent.py, system.py, rag.py, ...)         │
├─────────────────────────────────────────────────────────────┤
│  CONFIG       │  Environment and runtime configuration.     │
│  LAYER        │  (settings.py)                              │
├─────────────────────────────────────────────────────────────┤
│  LOGGING      │  Structured logging, trace context.         │
│  LAYER        │  (preparation for future implementation)    │
├─────────────────────────────────────────────────────────────┤
│  EXCEPTIONS   │  Domain-specific exception hierarchy.       │
│  LAYER        │  (preparation for future implementation)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Layer Responsibilities

### 6.1 FastAPI Layer

- Accept HTTP requests and return HTTP responses.
- Validate incoming requests against Pydantic models.
- Serialise responses into the expected format.
- Never contain business logic, orchestration logic, or tool execution.
- Never import from LangGraph, Tools, Memory, or LLM directly.

### 6.2 Service Layer

- Coordinate business workflows by calling the Runtime.
- Translate between API concepts and system concepts.
- Remain thin. If a service method grows beyond a few lines, move logic into the appropriate layer.
- Never import from LangGraph, Tools, or LLM directly.

### 6.3 Runtime Layer

- Act as the sole public entry point into Jarvis.
- Construct initial LangGraph state from incoming parameters.
- Invoke the LangGraph graph and return the result.
- Never contain orchestration logic, business logic, or tool execution.
- Never import from Tools, Memory, or LLM directly.

### 6.4 Orchestration Layer (LangGraph)

- Define the state machine topology (nodes, edges, routing).
- Route execution to the next appropriate node.
- Keep nodes small. A node should decide *what* to do next, not *how* to do it.
- Never contain business logic.
- Never access storage, FastAPI, or LLM directly (except the agent node, which calls the LLM).
- Never call tools directly — always through the Tool Engine.

### 6.5 Tool Engine

- Execute tools by name with provided arguments.
- Log every tool invocation with parameters and result.
- Enforce security policies, audit requirements, and rate limits (future).
- Never bypass the Registry — always look up tools through it.
- Never contain business logic specific to any tool.

### 6.6 Tool Registry

- Maintain a map of tool names to tool instances.
- Support registration of new tools at initialisation time.
- Support dynamic discovery of available tools (for prompt generation, future).
- Never execute tools. Registration and discovery only.

### 6.7 Tools (Individual)

- Contain all business logic.
- Validate their own input arguments.
- Return structured results.
- Be independently testable.
- Never depend on other tools.
- Never call the LLM, access memory, or interact with FastAPI.

### 6.8 Infrastructure Services

| Service | Responsibility | Accessed By |
|---|---|---|
| Memory | Session storage and retrieval | MemoryManager → nodes |
| LLM | Model inference | Agent node |
| Prompts | Prompt templates | Agent node |
| Config | Environment configuration | All layers (read-only) |
| Logging | Structured log output | All layers |
| Exceptions | Domain exception hierarchy | All layers |

---

## 7. Dependency Rules

### 7.1 Allowed Dependencies

| Layer | May Depend On |
|---|---|
| FastAPI | Service, Config, Exceptions |
| Service | Runtime, Config, Exceptions |
| Runtime | LangGraph, Config, Exceptions |
| LangGraph | Tool Engine, LLM, Prompts, Memory, Config, Exceptions |
| Tool Engine | Registry, Config, Exceptions, Logging |
| Registry | Tools, Config, Exceptions |
| Tools | Config, Exceptions |
| Memory | Config, Exceptions |
| LLM | Config, Exceptions |
| Prompts | (none — pure templates) |

### 7.2 Forbidden Dependencies

| Violation | Why |
|---|---|
| FastAPI → LangGraph | Skips Runtime. Breaks single-entry-point invariant. |
| FastAPI → Tools | Skips entire execution chain. Breaks security enforcement. |
| Service → LangGraph | Skips Runtime. Bypasses state construction. |
| Service → Tools | Skips orchestration and execution gates. |
| Runtime → Tools | Skips orchestration. Business logic would bypass LangGraph. |
| LangGraph → FastAPI | Reverse dependency. Web framework is transport, not logic. |
| Tools → LangGraph | Tools must not control orchestration. |
| Tools → Tools | Cross-tool coupling. Each tool is independent. |
| Tools → Memory | Memory is accessed through nodes, not directly by tools. |
| Tools → LLM | Tools execute; they do not reason. |
| Memory → LangGraph | Memory is a service consumed by orchestration, not the reverse. |

---

## 8. Data Flow

### 8.1 Direction of Dependencies

```
FastAPI  →  Service  →  Runtime  →  LangGraph  →  Tool Engine  →  Registry  →  Tools
                                              ↘              ↗
                                          Infrastructure Services
                                          (Memory, LLM, Prompts,
                                           Config, Logging, Exceptions)
```

### 8.2 Data Flow Principle

Data flows along the dependency chain — from higher layers to lower layers — and results flow back up through the call stack. The LangGraph state object (`State` TypedDict) is the carrier: it is constructed by the Runtime, mutated by nodes, and read by the Runtime on return.

```
Request  →  [FastAPI → Service → Runtime]  →  LangGraph.invoke(state)
                                                      │
                                          ┌───────────┴───────────┐
                                          ▼                       ▼
                                     Agent Node              Tool Node
                                          │                       │
                                          ▼                       ▼
                                        LLM                  Tool Engine
                                          │                       │
                                          ▼                       ▼
                                      JSON action             Registry → Tool
                                          │                       │
                                          └───────────┬───────────┘
                                                      ▼
                                              state["response"]
                                                      │
                                                      ▼
              Response  ←  [Runtime → Service → FastAPI]
```

---

## 9. Request Lifecycle

A complete request follows this exact sequence:

```
Step  | Layer          | Action
──────|────────────────|──────────────────────────────────────────
  1   | FastAPI        | Receive HTTP POST /chat
  2   | FastAPI        | Validate request body against ChatRequest
  3   | FastAPI        | Call chat_service.chat(session_id, message)
  4   | Service        | Call jarvis.chat(session_id, message)
  5   | Runtime        | Construct State dict:
                         {session_id, message, action, observation, response}
  6   | Runtime        | Invoke graph.invoke(State)
  7   | LangGraph      | Route from START → agent node
  8   | Agent Node     | Build prompt: AGENT_PROMPT + message + observation
  9   | Agent Node     | Call llm.invoke(prompt)
 10   | LLM            | Return JSON (tool action or final response)
 11   | Agent Node     | Parse JSON. Set state["action"].
 12   | LangGraph      | Route: if action["type"] == "tool" → tool node
                         if action["type"] == "final" → END
 13   | Tool Node      | Call engine.execute(action["tool"], **action["arguments"])
 14   | Tool Engine    | Look up tool: registry.get(tool_name)
 15   | Tool Engine    | Execute: tool.execute(**args)
 16   | Tool Engine    | Return result
 17   | Tool Node      | Set state["observation"] = {result}
 18   | LangGraph      | Loop back to step 8 (agent node with observation)
 19   | LangGraph      | When action["type"] == "final", route to END
 20   | Runtime        | Read state["response"]
 21   | Service        | Return response string
 22   | FastAPI        | Serialise ChatResponse, return HTTP 200
```

---

## 10. Component Responsibilities

### 10.1 FastAPI Components

| Component | Responsibility |
|---|---|
| `routes.py` | Define HTTP endpoints. Delegate to service layer. |
| `request_models.py` | Pydantic models for request validation. |
| `schemas.py` | Pydantic models for response serialisation. |
| `dependencies.py` | FastAPI dependency injection (auth, session resolution). |

### 10.2 Service Components

| Component | Responsibility |
|---|---|
| `chat_service.py` | Accept session_id + message, delegate to Runtime, return response. |

### 10.3 Runtime Components

| Component | Responsibility |
|---|---|
| `runtime.py` | Construct initial state, invoke LangGraph graph, return result. |

### 10.4 LangGraph Components

| Component | Responsibility |
|---|---|
| `graph.py` | Define StateGraph topology, nodes, edges, routing function. |
| `state.py` | Define State TypedDict schema. |
| `nodes/agent.py` | Build LLM prompt, invoke LLM, parse JSON action. |
| `nodes/tool_node.py` | Receive action dict, call Tool Engine, return observation. |

### 10.5 Tool System Components

| Component | Responsibility |
|---|---|
| `tool.py` | Abstract base class defining the Tool interface. |
| `engine.py` | Execute tools by name. Single execution gate. |
| `registry.py` | Register and discover tools. |
| `calculator.py` | Evaluate mathematical expressions. |
| `datetime_tool.py` | Return current date and time. |
| `file_reader.py` | Read file contents (sandboxed to approved paths). |
| `python_runner.py` | Execute Python code in a restricted sandbox. |

### 10.6 Infrastructure Service Components

| Component | Responsibility |
|---|---|
| `Memory/manager.py` | Provide session memory. Interface to storage. |
| `Memory/storage.py` | In-memory session storage (replaceable). |
| `Memory/persistence.py` | Future: database-backed persistent storage. |
| `LLM/client.py` | LLM model inference. Replaceable client. |
| `Prompts/agent.py` | Agent system prompt template. |
| `Config/settings.py` | Environment configuration. |
| `Exceptions/exceptions.py` | Domain exception hierarchy. |

---

## 11. Interface-Driven Design

Jarvis achieves replaceability through interface contracts. Every major component defines its boundary through an abstract class or protocol.

### 11.1 Tool Interface

```python
class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        ...
```

Every tool implements this interface. The Tool Engine depends on the interface, not on concrete tool classes.

### 11.2 Future Interfaces (Conceptual)

```python
class LLMProvider(ABC):
    @abstractmethod
    def invoke(self, messages: list[BaseMessage]) -> BaseMessage:
        ...

class MemoryBackend(ABC):
    @abstractmethod
    def get_memory(self, session_id: str) -> ChatMessageHistory:
        ...

    @abstractmethod
    def save(self, session_id: str, memory: ChatMessageHistory) -> None:
        ...
```

These interfaces are not yet implemented but are documented here as architectural commitments. Any LLM provider or memory backend that satisfies the interface can be plugged in without changing the orchestration layer.

### 11.3 Interface Rules

- Every public module must expose an interface (abstract class or Protocol).
- Internal implementation details must not leak through the interface.
- The interface is the contract. Breaking the interface is a breaking change.
- Multiple implementations of the same interface are always possible.

---

## 12. Extension Strategy

### 12.1 Adding a New Tool

1. Create a new class that inherits from `Tool`.
2. Set `name` and `description`.
3. Implement `execute(**kwargs)`.
4. Register the tool in `ToolRegistry.__init__`.
5. Update the prompt template to include the new tool's name and schema.

No other changes to the architecture are required. The new tool is automatically discoverable, executable, and testable.

### 12.2 Adding a New LLM Provider

1. Implement the `LLMProvider` interface.
2. Configure the active provider via environment configuration.
3. The orchestration layer uses the configured provider — no code changes.

### 12.3 Adding a New Memory Backend

1. Implement the `MemoryBackend` interface.
2. Inject the backend into `MemoryStorage`.
3. The `MemoryManager` exposes the backend transparently.

### 12.4 Future Plugin Architecture

In future horizons, Jarvis will support a plugin system where:

- Tools can be installed as external packages that self-register.
- Plugins declare their capabilities through a manifest.
- The Registry discovers plugins at startup or dynamically at runtime.
- Plugins are sandboxed by the Tool Engine with configurable permissions.

The current architecture supports this evolution: the Registry already abstracts registration, and the Engine already enforces execution boundaries. Adding plugin discovery requires adding a plugin loader — not changing the core.

---

## 13. Architectural Constraints

1. **One entry point.** The Runtime is the only public API. No other module exposes a public interface for external callers.
2. **No circular dependencies.** The dependency graph must remain a DAG. Tools may not depend on other tools. LangGraph may not depend on FastAPI.
3. **No direct storage access.** Storage backends are accessed through MemoryManager only.
4. **No direct tool calls.** Tools are called through Tool Engine → Registry → Tool. No other code path may invoke a tool.
5. **No LLM coupling.** The LLM client is swappable. No code outside the LLM layer imports a specific provider.
6. **Session isolation.** Session data is partitioned by session_id. No component may access data from another session.
7. **Auditability.** Every tool execution is logged with tool name, arguments (excluding secrets), and result.
8. **Testability.** Every component must be testable in isolation by mocking its dependencies through interfaces.

---

## 14. Anti-Patterns

These patterns are explicitly forbidden:

| Anti-Pattern | Why | Solution |
|---|---|---|
| **God Module** | A module that does everything (e.g., a single `agents.py` file). | Split by responsibility. One file = one concern. |
| **Callback Hell** | LangGraph nodes that call other LangGraph nodes directly. | Use the graph router. Nodes never call nodes. |
| **Magic Imports** | `from app.Tools import *` or dynamic imports. | Explicit imports only. |
| **Global State** | Module-level mutable state shared across sessions. | Session-bound state through MemoryManager. |
| **LLM in Tools** | A tool that calls the LLM directly. | Tools execute. The agent node reasons. |
| **Bypassing the Engine** | Calling `registry.get().execute()` instead of `engine.execute()`. | Always go through the Engine. |
| **Config in Code** | Hardcoded API keys, model names, or paths. | Use Config/settings.py with environment variables. |
| **Silent Errors** | Catching exceptions without logging. | Every exception is logged with context. |
| **Synchronous Blocking** | Long-running operations that block the event loop. | Use async where appropriate (future). |

---

## 15. Quality Attributes

| Attribute | Requirement | How Architecture Enforces It |
|---|---|---|
| **Extensibility** | New tools, LLMs, or memory backends without core changes | Interface-driven design; Registry for discovery |
| **Maintainability** | Any engineer can modify any module | Strict layering; single responsibility; small modules |
| **Security** | No RCE, no unauthorised file access, no secret leakage | Tool Engine as execution gate; no direct file access; fail-closed |
| **Observability** | Every action is traceable from logs | Logging at every layer; Engine logs every tool call |
| **Reliability** | No silent failures; session isolation | Fail-closed design; MemoryManager enforces isolation |
| **Testability** | Every component testable in isolation | Interface-based dependencies; no global state |
| **Performance** | Sub-second response for non-tool queries | Minimal layering overhead; thin service layer. Asynchronous execution should be preferred for I/O-bound operations while preserving architectural boundaries. |
| **Replaceability** | Any component can be swapped | Interface contracts for LLM, Memory, Tools |

---

## 16. Observability as an Architectural Concern

Observability is not a feature — it is a structural property of the architecture.

### 16.1 What Must Be Observable

- Every LLM invocation (prompt, response, latency, token count).
- Every tool execution (tool name, arguments, result, duration).
- Every graph state transition (from node, to node, state snapshot).
- Every error (error type, message, stack trace, session context).
- Every request (method, path, session_id, duration, status code).

### 16.2 Trace Context

Every log line must include:

- `session_id` — the session context.
- `request_id` — the request context.
- `component` — the layer or module that produced the log.
- `timestamp` — ISO 8601 with timezone.
- `level` — DEBUG, INFO, WARN, ERROR.

### 16.3 Audit Trail

The Tool Engine maintains an audit log of every tool execution. This log is immutable (append-only) and includes:

- Tool name and version.
- Arguments (with secrets redacted).
- Result (truncated if large).
- Session ID and user identity (future).
- Timestamp and duration.

---

## 17. Future Evolution

### 17.1 Multi-Agent Support

The same LangGraph orchestration layer will support multiple agent nodes. Agents will be able to delegate tasks to other agents. The graph topology changes — the architecture does not.

Key changes:
- Multiple agent nodes, each with a defined role and capability.
- Agent-to-agent routing in the graph router.
- Shared state across agents within the same session.

### 17.2 MCP Integration

The Model Context Protocol (MCP) will be supported as a tool adapter. MCP servers will be registered in the Tool Registry and executed through the Tool Engine — just like native tools.

Key changes:
- An `MCPToolAdapter` that wraps an MCP server as a `Tool`.
- The Registry discovers MCP tools at startup.
- No changes to the Engine, LangGraph, or Runtime.

### 17.3 Distributed Deployment

The Runtime will be deployable behind a load balancer. Session state moves from in-memory to a shared backend (database, Redis). The Runtime API remains unchanged.

Key changes:
- `MemoryStorage` uses a database backend instead of an in-memory dict.
- Sessions are distributed and resilient to node failure.
- The Runtime remains stateless — all state is in memory.

### 17.4 Event-Driven Architecture

Future versions of Jarvis may introduce an event-driven architecture for long-running and asynchronous workloads.

Potential additions include:

- Background workers
- Event bus
- Scheduled task execution
- Queue-based processing
- Distributed event handling

These capabilities must integrate through existing architectural boundaries rather than bypassing the Runtime or Tool Engine.

--- 

## 18. Architectural Versioning

Jarvis architecture evolves through controlled iterations.

- Major versions may introduce new architectural capabilities or retire obsolete patterns.
- Minor versions refine responsibilities while preserving public interfaces.
- Deprecated architectural patterns remain documented until they are fully removed.
- Architectural evolution must preserve backward compatibility whenever practical.

---

*This architecture defines how Jarvis is built. Every implementation detail must conform to these boundaries, rules, and principles.*
# Architecture Overview — Jarvis AIOS v1.0

Jarvis AIOS Placement Edition is an extensible, production-grade AI Operating System designed around a strict 7-layer decoupled architecture.

---

## 1. Core Architecture Hierarchy

```
FastAPI Gateway (/api/v1/*)
      │
      ▼
Runtime Manager Layer
      │
      ▼
LangGraph Orchestration Runtime
      │
      ▼
Tool Engine (Isolated Execution Sandbox)
      │
      ▼
Tool Registry (Dynamic Capabilities)
      │
      ▼
Individual Tools & MCP Adapters
      │
      ▼
LLM Engine (Multi-Provider Model Routing)
```

---

## 2. Layer Definitions & Principles

1. **FastAPI Gateway:** Public API entry point. Validates request schemas via Pydantic V2, enforces JWT authentication, and applies RBAC policy permissions.
2. **Runtime Manager Layer:** Central orchestrator connecting external API requests to internal subsystem managers without exposing internal state.
3. **LangGraph Runtime:** Orchestrates complex agent graphs and visual workflow AST definitions using stateful graph nodes.
4. **Tool Engine:** Executes tools in isolated sandboxes with strict parameter validation and failure handling.
5. **Tool Registry:** Dynamic catalog of system capabilities, custom Python tools, and Model Context Protocol (MCP) tools.
6. **Individual Tools:** Independent business logic implementations.
7. **LLM Engine:** Multi-provider model routing adapter connecting to OpenAI, Anthropic, Google Gemini, Ollama, and local models.

---

## 3. Subsystem Architecture Map

```
                ┌─────────────────────────────────────────┐
                │          WorkspaceShell UI              │
                └────────────────────┬────────────────────┘
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         │                                                       │
  ┌──────▼──────┐   ┌─────────────┐   ┌─────────────┐   ┌────────▼────┐
  │ Tool Studio │   │Prompt Studio│   │ RAG Studio  │   │Agent Studio │
  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └────────┬────┘
         │                 │                 │                   │
  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐   ┌────────▼────┐
  │Memory Studio│   │Model Studio │   │Workflow Studio│ │Deployment Studio│
  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
```

---

## 4. Key Architectural Guarantees

- **Architecture Over Implementation:** Strict layer decoupling. Lower layers never import from upper layers.
- **Session-Based Memory:** `MemoryManager` abstracts storage, preserving compatibility with SQLite, PostgreSQL, and vector stores.
- **Vault Secret Isolation:** Secrets encrypted at rest using XOR/AES and masked in all REST payloads.

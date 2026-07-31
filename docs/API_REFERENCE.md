# API Reference — Jarvis AIOS v1.0

Jarvis AIOS exposes a RESTful API generated via OpenAPI (Swagger/ReDoc) under `/api/v1/*`. Interactive documentation is served automatically at `http://localhost:8000/docs`.

---

## 1. Architectural Overview & Endpoint Groupings

All REST requests route through FastAPI middleware (`app/main.py`), which delegates to domain-specific services (`FastAPI -> Runtime -> Subsystem Manager -> Tool Engine / LangGraph`).

### Core Base URL
`http://localhost:8000/api/v1`

---

## 2. API Subsystem Endpoint Reference

### 2.1 Tool Studio (`/api/v1/tools`)
- `GET /api/v1/tools` — List all registered tools in the Tool Registry.
- `POST /api/v1/tools/execute` — Execute a tool via the isolated Tool Engine.
- `POST /api/v1/tools/register` — Register a custom tool or MCP server.

### 2.2 Prompt Studio (`/api/v1/prompts`)
- `GET /api/v1/prompts` — List prompt templates.
- `POST /api/v1/prompts` — Create a new prompt template.
- `POST /api/v1/prompts/compile` — Compile prompt template with dynamic inputs.

### 2.3 RAG Studio (`/api/v1/rag`)
- `GET /api/v1/rag/collections` — List vector search collections.
- `POST /api/v1/rag/ingest` — Ingest document text or files.
- `POST /api/v1/rag/search` — Perform hybrid BM25 + Vector + RRF search.

### 2.4 Agent Studio (`/api/v1/agents`)
- `GET /api/v1/agents` — List agent configurations.
- `POST /api/v1/agents` — Create ReAct or Plan-Execute agent.
- `POST /api/v1/agents/{id}/invoke` — Invoke agent with user message.

### 2.5 Memory Studio (`/api/v1/memory`)
- `GET /api/v1/memory/timeline` — Query multi-tier memory items.
- `POST /api/v1/memory/search` — Perform semantic memory recall search.
- `DELETE /api/v1/memory/{id}` — Forget specific memory item.

### 2.6 Model Studio (`/api/v1/models`)
- `GET /api/v1/models/providers` — List LLM provider configurations.
- `POST /api/v1/models/providers` — Add or update LLM provider API keys.
- `POST /api/v1/models/benchmark` — Run latency and token cost benchmarks.

### 2.7 Workflow Studio (`/api/v1/workflows`)
- `GET /api/v1/workflows` — List visual workflows.
- `POST /api/v1/workflows` — Save visual DAG workflow definitions.
- `POST /api/v1/workflows/compile` — Compile DAG visual definition into LangGraph StateGraph AST.
- `POST /api/v1/workflows/{id}/execute` — Trigger workflow execution.
- `GET /api/v1/workflows/{id}/stream` — SSE stream live execution logs and telemetry events.

### 2.8 Deployment Studio (`/api/v1/deployments`)
- `GET /api/v1/deployments/environments` — List deployment environments (prod, staging, dev).
- `GET /api/v1/deployments/targets` — List target provider clusters (Docker, K8s, Railway).
- `GET /api/v1/deployments/{env_id}/health` — Retrieve cluster CPU/RAM and container health probes.
- `POST /api/v1/deployments/rollout` — Trigger Blue/Green or Canary version rollout.
- `POST /api/v1/deployments/rollback` — Trigger sub-5-second 1-click release rollback.
- `GET /api/v1/deployments/secrets` — List masked vault secrets.
- `POST /api/v1/deployments/secrets` — Save AES/XOR encrypted secret key to vault.
- `POST /api/v1/deployments/backups` — Generate manual DB snapshot backup.
- `POST /api/v1/deployments/backups/restore` — Restore database snapshot.

---

## 3. OpenAPI JSON Schema Export

To dump the complete live OpenAPI schema programmatically:
```bash
curl http://localhost:8000/openapi.json -o openapi.json
```

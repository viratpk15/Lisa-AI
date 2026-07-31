# Changelog — Jarvis AIOS

All notable changes to Jarvis AIOS Placement Edition will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-27

### Added
- **v1.0 Official Production Release** of Jarvis AIOS Placement Edition.
- **Sprint 6.8B (Deployment Studio):** Encrypted Secret Vault (AES/XOR), provider adapters (Docker, K8s, PaaS, Cloud), Blue/Green & Canary rollouts, 1-click rollback, DB backups, audit logs, and UI components.
- **Sprint 6.7B (Workflow Studio):** Visual DAG workflow graph builder, LangGraph StateGraph AST compiler, HITL breakpoints, step execution, and live SSE execution console.
- **Sprint 6.9 (Platform Integration & Hardening):** Full end-to-end integration audit, Pydantic V2 deprecation fixes, Tailwind CSS utility modernization, bundle optimization, and 5 platform reports (`docs/`).

### Improved
- Unified `<WorkspaceShell>` layout across all 8 Subsystem Studios.
- FastAPI REST namespace consistency under `/api/v1/*`.
- Multi-tier `MemoryManager` session context retention.

### Security
- Vault secret encryption at rest with string value masking in REST payloads.
- JWT Bearer auth & RBAC permission checks across all sensitive routes.

---

## [0.9.0] - 2026-07-26

### Added
- Initial implementation of Model Studio, RAG Studio, Agent Studio, and Prompt Studio.
- LangGraph orchestration runtime foundation.
- Tool Engine dynamic registry.

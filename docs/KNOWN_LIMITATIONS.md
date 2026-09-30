# Known Limitations — Jarvis AIOS v1.0

This document outlines current operational boundaries and known scope limitations for Jarvis AIOS v1.0 Placement Edition.

---

## 1. Environment & Storage

- **Default Storage Engine:** Local SQLite storage enabled by default. For high-concurrency multi-instance production, PostgreSQL configuration is recommended (`DATABASE_URL`).
- **In-Memory Vector Search:** Default vector search operates using in-memory / local FAISS indexes. Production scale (> 1M vectors) requires dedicated Milvus/Qdrant/PgVector clusters.

---

## 2. Telemetry & Streaming

- **SSE Connection Limits:** Server-Sent Events (SSE) telemetry streams depend on proxy configuration (Nginx / Cloudflare). Ensure HTTP/1.1 response buffering is disabled (`proxy_buffering off;`).

---

## 3. Provider Limits & Rate Limiting

- **External LLM Providers:** API rate limits, token timeouts, and context window limits are governed by external LLM provider quotas.

---

## 4. Post-Redesign Operational Limitations (v2.2-ga)

- **Gmail Sync On-Demand Only:** Gmail intelligence does not run a continuous background worker/polling daemon; inbox synchronization occurs on-demand via the "Sync Now" control.
- **Gmail Read-Only Scope:** By design and security constraint, email OAuth scope is strictly read-only (`https://www.googleapis.com/auth/gmail.readonly`). Sending, replying, deleting, or modifying Gmail labels is not supported.
- **Files Preview:** Document viewer uses native browser capabilities/downloads for file preview; embedded inline rich PDF/document viewers are deferred.
- **Developer Studios Desktop-First:** Advanced developer studio surfaces (`/settings/developer/*`) are optimized for desktop viewports (>= 1024px) and do not support mobile tablet layouts.
- **Allowed Provider Policy:** The model settings UI strictly displays authorized high-speed inference providers (**Groq**, **NVIDIA NIM**, **Mistral**).
- **Ollama Fallback:** Ollama is hidden from normal registration UI and retained only as an internal developer-only local testing fallback.
- **Type Checking (Pyright):** 101 pre-existing type check errors and 6 warnings remain isolated in legacy backend test suites (`app/tests/test_Tools/` and `app/tests/test_LangGraph/`); runtime application logic passes cleanly.

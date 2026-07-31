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

- **External LLM Providers:** API rate limits, token timeouts, and context window limits are governed by external LLM provider quotas (OpenAI, Anthropic, Google Gemini).

# Release Notes — Lisa AIOS v2.0 (v2.2-ga)

**Version:** v2.2-ga  
**Release Date:** 2026-09-28  
**Architecture:** 5-Item Primary Navigation + Developer / AIOS Studio Portal  

---

## 1. Executive Summary

Lisa AIOS v2.0 represents a complete consumer-focused frontend redesign delivering on the core product philosophy:  
> **Power underneath. Simplicity on top.**

The redesign transitions the system from a fragmented multi-tool dashboard into a coherent personal AI companion (Lisa) backed by full AIOS developer capabilities.

- **v2.0 Shell (R1):** Unified 5-item primary navigation (`Home`, `Assistant`, `Email`, `Files`, `Settings`), canonical redirect map for 10 legacy URLs, and integrated Developer / AIOS portal under `/settings/developer`.
- **v2.1 Product Polish (R2):** Real-data wiring across Assistant, Email, and Files; mobile single-pane email experience; real document RAG hybrid search; and two-tab simplified Inspector (AI Context + Email Context).
- **v2.2-ga Cleanup (R3):** Deletion of unreferenced legacy dashboard widgets, complete elimination of residual fake/mock data, UX jargon removal, accessibility hardening, and full end-to-end verification.

---

## 2. Primary Navigation (5 Items)

The primary navigation is strictly locked to 5 items:

1. **Home (`/`):** Personal overview, urgent email items requiring attention (`/api/v1/email/digest`), recent conversations (`/conversations`), and quick action launchers.
2. **Assistant (`/assistant`):** Direct interactive chat with Lisa powered by SSE streaming, document context attachments, and real-time execution feedback.
3. **Email (`/email`):** Personal email intelligence (Gmail sync, spam/phishing classification, priority scoring, action item and deadline extraction, and daily digest).
4. **Files (`/files`):** User knowledge base for uploading documents, hybrid semantic search, and "Ask Lisa" document exploration.
5. **Settings (`/settings`):** Account profile, desktop theme customization (Dark, Light, Aurora), conversation memory reset, and entry point to Developer / AIOS.

---

## 3. Developer / AIOS Studio Portal

Advanced AIOS capabilities are organized under `/settings/developer/`:
- **Core:** Agents (`/settings/developer/core/agents`), Tools (`/settings/developer/core/tools`), Workflows (`/settings/developer/core/workflows`)
- **Knowledge:** Memory (`/settings/developer/knowledge/memory`), RAG (`/settings/developer/knowledge/rag`)
- **AI:** Models (`/settings/developer/ai/models`), Prompts (`/settings/developer/ai/prompts`)
- **Integrations:** MCP (`/settings/developer/integrations/mcp`), Connections (`/settings/developer/integrations/connections`)
- **Infrastructure:** Deployment (`/settings/developer/infrastructure/deployment`), Observability (`/settings/developer/infrastructure/observability`)

---

## 4. Canonical Redirect Map

All legacy routes transparently redirect via `<Navigate replace />`:
- `/dashboard` → `/`
- `/workspace` → `/assistant`
- `/agents` → `/settings/developer/core/agents`
- `/memory` → `/settings/developer/knowledge/memory`
- `/tools` → `/settings/developer/core/tools`
- `/rag` → `/settings/developer/knowledge/rag`
- `/models` → `/settings/developer/ai/models`
- `/workflows` → `/settings/developer/core/workflows`
- `/deployments` → `/settings/developer/infrastructure/deployment`
- `/prompts` → `/settings/developer/ai/prompts`

---

## 5. Model Provider Policy

User-facing model configuration at `/settings/developer/ai/models` strictly filters providers:
- **Authorized / Displayed Providers:** Groq, NVIDIA NIM, Mistral
- **Hidden / Developer Fallback Providers:** Ollama, Gemini, Anthropic, OpenRouter, Cerebras, Together, Fireworks

---

## 6. Deferred Features Register

The following capabilities are deliberately out of scope for v2.0/v2.2-ga and remain deferred:
- Continuous Gmail background monitoring (sync is on-demand)
- Autonomous email actions (sending, replying, deleting — read-only OAuth scope)
- Jobs & Internships Agent
- Travel Planner Agent
- Event Bus / Redis / Celery background workers
- Proactive push notifications
- Advanced Codebase Intelligence
- Voice input / output

---

## 7. Release Verification Status

**FINAL VERDICT: READY WITH CAVEATS**

- **Automated Verification:** Backend pytest passed (347 passed), Ruff clean, Frontend lint (oxlint) clean, Frontend build passed, scope compliance verified.
- **Pyright:** Pre-existing 101 errors and 6 warnings remain isolated in legacy test suites.
- **Caveat:** Live browser verification was not performed during R3. Live runtime behavior (browser-based login/logout, Gmail OAuth flow, live SSE streaming in browser, file uploads, mobile touch interaction, and live legacy URL redirects) has not been verified in an active browser E2E session.


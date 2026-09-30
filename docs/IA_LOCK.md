# Lisa AIOS Information Architecture Lock

**Version:** R0
**Date:** 2026-09-27
**Status:** LOCKED — Do not modify source code based on this document without explicit authorization.
**Author:** R0 Audit (Antigravity)

---

## 1. Purpose

This document is the **canonical single source of truth** for the Lisa AIOS frontend redesign. Produced by read-only audit of the repository after Email Agent completion (Prompts 1–3). No source code was modified.

**Product philosophy locked:**
> Power underneath. Simplicity on top.

**Primary navigation locked (5 items):**

```
Lisa
├── Home          (/  — was /dashboard)
├── Assistant     (/assistant — was /workspace)
├── Email         (/email — unchanged)
├── Files         (/files — unchanged)
└── Settings      (/settings — expanded)
    ├── Account
    ├── Appearance
    ├── Memory
    └── Developer / AIOS
        ├── Overview
        ├── Core → Agents, Tools, Workflows
        ├── Knowledge → Memory, RAG
        ├── AI → Models, Prompts
        ├── Integrations → MCP, Connections
        └── Infrastructure → Deployment, Observability
```

Every redesign prompt (R1 / R2 / R3) must conform to this document.

---

## 2. Current Application Audit

**Stack:** React 19 + Vite + TypeScript, Tailwind CSS v4, Framer Motion, TanStack Query v5, Zustand, FastAPI, LangGraph, SQLAlchemy, SQLite (dev), Alembic, Pydantic.

**Key structural files:**
- `frontend/src/App.tsx` — router root; 14 lazy-loaded page features
- `frontend/src/components/layout/AppShell.tsx` — shell: sidebar + topbar + inspector + status bar
- `frontend/src/components/layout/InspectorPanel.tsx` — right panel, 8 tabs (all mocked)
- `frontend/src/components/common/CommandPalette.tsx` — ⌘K launcher (14 commands, 5 dead)
- `frontend/src/features/` — 14 feature directories
- `frontend/src/services/` — API client, SSE, auth store, TanStack query hooks
- `frontend/src/providers/` — ThemeProvider (dark/light/aurora), RootProvider (QueryClient)
- `backend/app/` — 24 subdirectories: FastAPI, LangGraph, ToolEngine, MCP, RAG, Memory, Observability, Deployments

**Current post-login default redirect:** `/dashboard`

---

## 3. Current Route Inventory

All routes behind `<ProtectedRoute>`. `/auth` is the only `<AnonymousRoute>`.

| Route | Component | File | Sidebar Group | Real/Mock | Backend | User Value | Target |
|---|---|---|---|---|---|---|---|
| `/auth` | AuthPage | `Auth/AuthPage.tsx` | Public | REAL | `/auth/*` | Login/Register | Keep `/auth` |
| `/` | → redirect | `App.tsx` | — | — | — | — | → `/` Home |
| `/dashboard` | DashboardPage | `Dashboard/DashboardPage.tsx` | Overview | HYBRID (mostly MOCKED) | partial | Attention center | → `/` Home |
| `/workspace` | WorkspacePage | `Workspace/WorkspacePage.tsx` | Overview | REAL | `/chat/stream`, `/conversations/*` | AI chat | → `/assistant` |
| `/agents` | AgentsPage | `Agents/AgentsPage.tsx` | Intelligence | REAL (studio) | `/agents/*` | Agent builder | → `/settings/developer/agents` |
| `/memory` | MemoryPage | `Memory/MemoryPage.tsx` | Intelligence | REAL (studio) | `/memory/*` | Memory inspection | → `/settings/developer/memory` |
| `/email` | EmailPage | `Email/EmailPage.tsx` | Personal Agents | REAL | `/api/v1/email/*` | Email intelligence | Keep `/email` |
| `/files` | FilesPage | `Files/FilesPage.tsx` | OS Resources | MOCKED | `/files/*`, RAG | File upload | Keep `/files` |
| `/tools` | ToolsPage | `Tools/ToolsPage.tsx` | OS Resources | REAL (studio) | `/tools/*` | Tool registry | → `/settings/developer/tools` |
| `/rag` | RAGPage | `RAG/RAGPage.tsx` | (no nav) | REAL (studio) | `/rag/*` | RAG engineering | → `/settings/developer/rag` |
| `/models` | ModelsPage | `Models/ModelsPage.tsx` | OS Resources | REAL (studio) | `/models/*` | Model registry | → `/settings/developer/models` |
| `/workflows` | WorkflowPage | `Workflows/WorkflowPage.tsx` | (no nav) | REAL | `/workflows/*` | Workflow studio | → `/settings/developer/workflows` |
| `/deployments` | DeploymentPage | `Deployments/DeploymentPage.tsx` | (no nav) | REAL | `/deployments/*` | Deployment studio | → `/settings/developer/deployment` |
| `/prompts` | PromptsPage | `Prompts/PromptsPage.tsx` | (no nav) | REAL | `/prompts/*` | Prompt studio | → `/settings/developer/prompts` |
| `/settings` | SettingsPage | `Settings/SettingsPage.tsx` | Configuration | PARTIAL | none for save | Preferences | Keep `/settings` |

**Note:** `/rag`, `/workflows`, `/deployments`, `/prompts` have no sidebar entry — unreachable via normal navigation.

---

## 4. Feature Inventory

| Feature | Status | Mocked Elements | Primary User | Action |
|---|---|---|---|---|
| **Dashboard** | HYBRID (mostly MOCKED) | Projects, Agents widget, Conversations, SystemHealth, Notifications, Timeline, Insights all hardcoded | Developer | REDESIGN as Home (real data only) |
| **Workspace / Assistant** | REAL | None | Everyone | RESTYLE + rename to `/assistant` |
| **Agents** | REAL | Analytics charts possibly | Developers | MOVE → Developer/Core/Agents |
| **Memory** | REAL | Debugger panel metrics possibly | Developers | MOVE → Developer/Knowledge/Memory |
| **Email** | REAL | Inspector panel email tab (static demo) | Everyone | POLISH |
| **Files** | MOCKED | Entire file table, all metric cards | Everyone | RESTYLE + wire to real API |
| **Tools** | REAL | Unknown per-tab | Developers | MOVE → Developer/Core/Tools |
| **RAG** | REAL | Analytics charts possibly | Developers | MOVE → Developer/Knowledge/RAG |
| **Models** | REAL | Unknown per panel | Developers | MOVE → Developer/AI/Models |
| **Workflows** | REAL | Unknown per panel | Developers | MOVE → Developer/Core/Workflows |
| **Deployments** | REAL | Unknown per panel | Developers | MOVE → Developer/Infrastructure/Deployment |
| **Prompts** | REAL | Unknown per panel | Developers | MOVE → Developer/AI/Prompts |
| **Settings** | PARTIAL (theme REAL; forms STATIC) | AI Engine fields, Security fields (no save handler) | Everyone | EXPAND |
| **Auth** | REAL | None | Everyone | KEEP |
| **MCP** | REAL (backend) / No frontend page | — | Developers | NEW page → Developer/Integrations/MCP |
| **Observability** | REAL (backend) / No frontend page | — | Developers | NEW page → Developer/Infrastructure/Observability |

---

## 5. Component Inventory

### Layout
| Component | File | Real Functionality | Action |
|---|---|---|---|
| AppShell | `components/layout/AppShell.tsx` | YES — nav, ⌘K, ⌘B, ⌘I, clock | RESTYLE (R1) |
| InspectorPanel | `components/layout/InspectorPanel.tsx` | PARTIAL — structure works, all data mocked | SIMPLIFY (R1) |

### Common
| Component | Action |
|---|---|
| `CommandPalette.tsx` | RESTYLE + update commands (R1) |
| `EmptyState.tsx`, `LoadingIndicator.tsx`, `Spinner.tsx` | KEEP |

### UI Primitives (shadcn — all KEEP)
`avatar`, `badge`, `button`, `card`, `dialog`, `dropdown-menu`, `input`, `scroll-area`, `separator`, `skeleton`, `textarea`, `tooltip`

### Workspace / Assistant Components (all KEEP for R2)
`Sidebar.tsx`, `Header.tsx`, `MessageArea.tsx`, `Composer.tsx`, `MessageBubble.tsx`, `CodeBlock.tsx`, `MarkdownRenderer.tsx`, `SearchModal.tsx`, `useVirtualizer.ts`

### Email Feature Components (all KEEP)
`EmailPage.tsx`, `InboxList.tsx`, `EmailDetail.tsx`, `DigestView.tsx`, `SenderAuthBadge.tsx`, `api.ts`, `queries.ts`

### Dashboard Widgets (RESTYLE in R2 as Home widgets)
`Hero.tsx`, `QuickActions.tsx`, `ContinueWorking.tsx`, `Projects.tsx`, `Agents.tsx`, `Conversations.tsx`, `SystemHealth.tsx`, `Notifications.tsx`, `Timeline.tsx`, `Insights.tsx`

### WorkspaceShell (shared developer studio shell — KEEP)
`features/Tools/components/shell/WorkspaceShell.tsx` — used by Agents, Memory, RAG, Tools

---

## 6. Real vs Mock Data Audit

| Surface | Data | Classification | Evidence |
|---|---|---|---|
| Hero greeting | Time-based + hardcoded `"Virat"` | STATIC | `Hero.tsx` L9 |
| ContinueWorking | 4 workspace cards, progress %, status | MOCKED | `ContinueWorking.tsx` L20–57 |
| Projects widget | 4 project cards, tasks, activity | MOCKED | `Projects.tsx` L20–65 |
| Agents widget | 6 agent cards, statuses, graph nodes | MOCKED | `Agents.tsx` L25–88 |
| Conversations widget | 3 conversation previews | MOCKED | `Conversations.tsx` L23–51 |
| System Health | 6 subsystem telemetry cards | MOCKED | `SystemHealth.tsx` L20–87 |
| Notifications | 4 notification items | MOCKED | `Notifications.tsx` L15–44 |
| Activity Timeline | 5 timeline events | MOCKED | `Timeline.tsx` L14–50 |
| Knowledge Insights | Model usage %, vector count, sparkline | MOCKED | `Insights.tsx` L8–21 |
| Files table | 3 hardcoded files | MOCKED | `FilesPage.tsx` L7–11 |
| Files stats | "14 Files", "842 Chunks", "98% Sync" | MOCKED | `FilesPage.tsx` L33,43,53 |
| Workspace switcher | 5 named workspaces | MOCKED | `AppShell.tsx` L105–111 |
| Status bar DB size | "1.2GB" | MOCKED | `AppShell.tsx` L566 |
| Status bar tokens | "Tokens: 1.4k" | MOCKED | `AppShell.tsx` L570 |
| Inspector Context tab | ses_92f8a1, token counts | MOCKED | `InspectorPanel.tsx` L57–68 |
| Inspector Memory tab | 1,824 Vectors, memory keys | MOCKED | `InspectorPanel.tsx` L80–95 |
| Inspector AI Thoughts | 3 reasoning steps | MOCKED | `InspectorPanel.tsx` L106–128 |
| Inspector Files tab | 4 listed files | MOCKED | `InspectorPanel.tsx` L138–166 |
| Inspector References | 3 hardcoded docs | MOCKED | `InspectorPanel.tsx` L178–199 |
| Inspector Tool Output | `read_directory()` result | MOCKED | `InspectorPanel.tsx` L205–221 |
| Inspector Debugger | Heap, latency metrics | MOCKED | `InspectorPanel.tsx` L228–242 |
| Inspector Email tab | PLACEMENT, score 95 | MOCKED (static demo) | `InspectorPanel.tsx` L258–303 |
| Settings AI Engine form | Model, temperature inputs | STATIC (no save) | `SettingsPage.tsx` L114–126 |
| Settings Security form | Directory, scope, prompt inputs | STATIC (no save) | `SettingsPage.tsx` L138–149 |
| **Email Inbox** | Email rows | **REAL** | TanStack Query → `/api/v1/email/list` |
| **Email Detail** | Body, analysis, verification | **REAL** | TanStack Query → `/api/v1/email/{id}` |
| **Email Digest** | Category counts, urgent list | **REAL** | TanStack Query → `/api/v1/email/digest` |
| **Auth** | Login/register forms | **REAL** | `/auth/login`, `/auth/register` |
| **Workspace conversations** | Conversation list + messages | **REAL** | TanStack Query + SSE |
| **All developer studios** | Agent/Memory/RAG/Tools/Models/etc. | **REAL** | Full API backends |

---

## 7. Backend Dependency Map

```
/auth
  └── FastAPI: /auth/login, /auth/register, /auth/me
        └── Auth.models (User, Session), bcrypt, JWT

/assistant (was /workspace)
  └── FastAPI: /chat/stream (SSE), /conversations/*, /conversations/{id}/messages
        └── LangGraph Runtime → Supervisor → ToolEngine → LLM
              ├── Memory (session context)
              ├── RAG (document retrieval)
              ├── MCP tools (GitHub, Filesystem, Web)
              └── LLM providers (Gemini, Anthropic)

/email
  └── FastAPI: /api/v1/email/* + /api/v1/auth/email/*
        └── email.sync, email.verify_sender, email.classify,
            email.summarize, email.extract_actions, email.digest
              ├── Gmail OAuth (google-auth-oauthlib)
              ├── Email DB models (emails, sender_verifications, analysis, digest_cache)
              └── LLM for classify/summarize/extract

/files
  └── FastAPI: /files/upload, /files/{session_id}
        └── RAG pipeline → chunker → embedder
              └── SQLite: documents, chunks, rag_embeddings

Developer surfaces (all existing, just relocated to /settings/developer/*)
  /agents     → FastAPI /agents/*, /agent-team/*, /executions/*
  /memory     → FastAPI /memory/*
  /tools      → FastAPI /tools/*, /mcp/*
  /rag        → FastAPI /rag/*, /datasets/*
  /models     → FastAPI /models/*, /provider-configs/*
  /workflows  → FastAPI /workflows/*
  /deployments→ FastAPI /deployments/*
  /prompts    → FastAPI /prompts/*
  Observability → backend/app/Observability/ (manager.py, models.py)
  MCP         → backend/app/MCP/ (mcp_manager.py, registry.py, health_monitor.py)
```

---

## 8. Authentication / SSE Preservation

### Authentication Flow

1. Protected route → `ProtectedRoute` checks `useAuthStore.isAuthenticated`
2. If not restored: `<LoadingIndicator>` (prevents flash)
3. If unauthenticated: stores `redirectTo`, navigates to `/auth`
4. `AuthPage` → `loginUser()` → `POST /auth/login` → stores JWT in `localStorage.jarvis_access_token`
5. Auth store: `isAuthenticated = true`, `user = decoded JWT`
6. `AnonymousRoute` redirects authenticated user to `/dashboard` (→ will become `/`)

**Token key:** `localStorage.jarvis_access_token`
**Token validation:** `_isRealJwt()` rejects placeholder tokens
**Expiry:** Client-side JWT decode + `exp` check on boot
**Logout:** `clearAuth()` → `logoutUser()` + clears Zustand
**401 guard:** Single-shot `_handlingUnauthorized` flag prevents duplicate redirects

**Files MUST NOT be modified during redesign:**
- `services/api/auth.ts`
- `services/store/authStore.ts`
- `services/api/apiClient.ts`
- `App.tsx` (ProtectedRoute / AnonymousRoute wrappers)
- `services/api/errors.ts`
- `providers/index.tsx`

### SSE Streaming

**Implementation:** `services/api/sse.ts` → `streamChatMessage()`
**Protocol:** `fetch()` + `ReadableStream` + `TextDecoder` (NOT EventSource)
**Endpoint:** `POST /chat/stream` with `{ session_id, message, attachment_ids, active_document_id, active_filename }`
**Event types:** `thinking`, `token`, `agent_state`, `tool_output`, `error`, `done`
**Cancellation:** `CancellationToken` with `AbortController`
**Error handling:** 401 → UnauthorizedError, 403 → ForbiddenError, abort → silent

**Files MUST NOT be modified during redesign:**
- `services/api/sse.ts`
- `features/Workspace/components/MessageArea.tsx`
- `features/Workspace/components/Composer.tsx`
- `features/Workspace/WorkspacePage.tsx`

---

## 9. Email Audit (Post Prompt 3)

### API Surface — All REAL

| Endpoint | Method | Frontend Call |
|---|---|---|
| `/api/v1/email/sync` | POST | `syncEmailApi()` |
| `/api/v1/email/list` | GET | `fetchEmailListApi()` |
| `/api/v1/email/{id}` | GET | `fetchEmailDetailApi()` |
| `/api/v1/email/{id}/classify` | POST | `classifyEmailApi()` |
| `/api/v1/email/{id}/summarize` | POST | `summarizeEmailApi()` |
| `/api/v1/email/{id}/extract-actions` | POST | `extractActionsEmailApi()` |
| `/api/v1/email/digest` | GET | `fetchEmailDigestApi()` |
| `/api/v1/auth/email/login` | GET | OAuth redirect |
| `/api/v1/auth/email/callback` | GET | OAuth callback |
| `/api/v1/auth/email/status` | GET | Connection status |

### Frontend Components — All REAL

| Component | Notes |
|---|---|
| `EmailPage.tsx` | 2-pane layout, URL tab sync |
| `InboxList.tsx` | Priority-grouped, category filter, skeleton states |
| `EmailDetail.tsx` | Body, analysis, verification; action buttons trigger real mutations |
| `DigestView.tsx` | Category volume cards, urgent list, action items |
| `SenderAuthBadge.tsx` | Visual from actual SPF/DKIM/DMARC fields |
| `queries.ts` | TanStack Query hooks with cache invalidation |
| `api.ts` | All 7 API methods wired |

### What Is Mocked
- `InspectorPanel.tsx` Email tab — static PLACEMENT/95 demo, not bound to selected email

### Gmail Prerequisites
- User must complete Gmail OAuth via `/api/v1/auth/email/login`
- Without OAuth, `/sync` errors → EmailPage surfaces error with retry
- Sync is on-demand only — no continuous background monitoring

---

## 10. Files / RAG Audit

### Files Page (`/files`) — MOCKED

`FilesPage.tsx` is a UI stub: 3 hardcoded file entries, hardcoded stats, "Add Document" button with no handler.

**Real backend exists:** `services/api/files.ts` + FastAPI `routes_files.py` handles multipart uploads + RAG pipeline processes them. The frontend was never wired.

### RAG Studio (`/rag`) — REAL but Unreachable

Full RAG studio: DatasetLibrary, DocumentExplorer, ChunkInspector, HybridSearchPanel, RAGEvaluationDashboard, RAGAnalyticsPanel, KnowledgeGraphViewer — all backed by `/rag/*`, `/datasets/*` API. Zero sidebar navigation entry.

### Concept Distinction

| User Concept | Developer Concept | Route |
|---|---|---|
| Upload a document | File ingestion → chunking → embedding | `/files` |
| Ask Lisa about a document | RAG retrieval in conversation | `/assistant` (attachment) |
| Inspect embeddings / eval | RAG Studio | → `/settings/developer/rag` |
| Manage filesystem access | Filesystem MCP | → `/settings/developer/integrations/mcp` |

---

## 11. MCP Audit

**Backend:** `backend/app/MCP/` — fully implemented (client, config, health_monitor, mcp_manager, registry, tool_adapter)
**Servers:** GitHub MCP, Filesystem MCP, custom servers
**Frontend:** No dedicated MCP page — partially exposed inside `/tools`

**Target:** `/settings/developer/integrations/mcp` — connected servers, per-server tool list, connect/disconnect controls

**Invariant:** Users should never see "MCP" — Lisa says "Checking GitHub…" or "Reading your files…"

---

## 12. Developer Surface Audit

Items currently in primary nav that must move to Developer / AIOS:

| Current Route | Target Route | Label |
|---|---|---|
| `/agents` | `/settings/developer/agents` | Agents |
| `/memory` | `/settings/developer/memory` | Memory |
| `/tools` | `/settings/developer/tools` | Tools |
| `/models` | `/settings/developer/models` | Models |
| `/rag` | `/settings/developer/rag` | RAG |
| `/workflows` | `/settings/developer/workflows` | Workflows |
| `/deployments` | `/settings/developer/deployment` | Deployment |
| `/prompts` | `/settings/developer/prompts` | Prompts |
| (inside /tools) | `/settings/developer/integrations/mcp` | MCP |
| (no page) | `/settings/developer/observability` | Observability |

### Target Developer / AIOS Route Structure

```
/settings/developer/
├── overview
├── core/
│   ├── agents        → AgentsPage (REUSE)
│   ├── tools         → ToolsPage (REUSE)
│   └── workflows     → WorkflowPage (REUSE)
├── knowledge/
│   ├── memory        → MemoryPage (REUSE)
│   └── rag           → RAGPage (REUSE)
├── ai/
│   ├── models        → ModelsPage (REUSE)
│   └── prompts       → PromptsPage (REUSE)
├── integrations/
│   ├── mcp           → NEW
│   └── connections   → NEW (Gmail OAuth status)
└── infrastructure/
    ├── deployment    → DeploymentPage (REUSE)
    └── observability → NEW wrapper
```

---

## 13. Settings Audit

**Current sections:**
1. **Appearance** — Theme switcher. **REAL and functional.**
2. **General AI Engine** — Model, Temperature, API Key inputs. **STATIC — no save handler.**
3. **Security Settings** — Directory, Scope, System Prompt inputs. **STATIC — no save handler.**
4. **Save button** — No onClick handler.

**Target Settings structure (R1):**

```
Settings
├── Account         — Profile, email, password (NEW)
├── Appearance      — Theme (REAL) + density/font prefs
├── Memory          — Clear memory, retention prefs
└── Developer / AIOS — Full developer portal (see §12)
```

**Deferred to later:** Notifications, Privacy (no backend exists).

---

## 14. Command Palette Audit

**File:** `components/common/CommandPalette.tsx` | **Trigger:** ⌘K | **Total commands:** 14

| ID | Name | Action | Status |
|---|---|---|---|
| nav-dash | Go to Dashboard | navigate("/dashboard") | LIVE (route changes to /) |
| nav-work | Go to Workspaces | navigate("/workspace") | LIVE (route changes to /assistant) |
| nav-agent | Go to AI Agents | navigate("/agents") | LIVE (route moves) |
| nav-mem | Go to Memory Manager | navigate("/memory") | LIVE (route moves) |
| nav-tool | Go to Tool Registry | navigate("/tools") | LIVE (route moves) |
| nav-set | Go to Settings | navigate("/settings") | LIVE |
| sys-sync | Sync Vector Database ⌘S | console.log | **DEAD** |
| sys-start | Start Code Orchestrator ⌥P | console.log | **DEAD** |
| sys-kernel | Restart AIOS Kernel ⇧K | console.log | **DEAD** |
| cmd-sidebar | Toggle Left Sidebar ⌘B | console.log | **DEAD** |
| cmd-search | Find in Files ⌘F | console.log | **DEAD** |
| cmd-prompt | Configure System Prompt ⌥P | navigate("/settings") | LIVE (shortcut collision with sys-start) |
| email-inbox | Open Inbox G I | navigate("/email") | LIVE |
| email-sync | Sync Email Now ⌥E | syncEmailApi() | LIVE |
| email-digest | Open Daily Digest G D | navigate("/email?tab=digest") | LIVE (shortcut collision with nav-dash) |

**Collisions:** `⌥P` shared by sys-start + cmd-prompt. `G D` shared by nav-dash + email-digest.

**R1 command restructure:**
```
Product: Home, Assistant, Email, Files, Settings
Developer / AIOS: Agents, Tools, Workflows, Memory, RAG, Models, Prompts, MCP, Deployment, Observability
```

---

## 15. Inspector Panel Audit

**File:** `components/layout/InspectorPanel.tsx`
**Toggle:** ⌘I | **Width:** 280px inline (≥1280px), overlay absolute (<1280px)
**Default tab:** AI Thoughts

| Tab | Data | Real? | Recommendation |
|---|---|---|---|
| context | Session ID, model, token counts | MOCKED | Wire in R2 from WorkspacePage state |
| email | SPF/DKIM/DMARC, classification | MOCKED (static demo) | Wire to selected email in R2 |
| memory | Vector count, memory keys | MOCKED | Wire from memory API or remove |
| files | 4 hardcoded files | MOCKED | Wire to session attachments in R2 |
| references | 3 hardcoded docs | MOCKED | Wire or remove |
| thoughts | 3 reasoning steps | MOCKED | Wire to `agent_state` SSE events in R2 |
| tools | `read_directory()` result | MOCKED | Wire to `tool_output` SSE events in R2 |
| debugger | Heap, latency metrics | MOCKED | Wire to `/health` or remove |

**R1 action:** Simplify to 2 visible tabs (AI Context, Email Context) surfacing only available data. Move full debugger content to Developer surface.

---

## 16. Design System

**CSS:** `src/styles/globals.css` (288 lines)
**Framework:** Tailwind CSS v4 + tw-animate-css + shadcn

### Themes

| Theme | Background | Primary |
|---|---|---|
| dark (default) | `hsl(240 10% 2%)` AMOLED black | `hsl(250 84% 67%)` Digital Violet |
| light | `hsl(0 0% 98%)` soft white | `hsl(220 90% 56%)` Blue |
| aurora | `hsl(270 15% 8%)` cybernetic | `hsl(265 80% 65%)` Electric Violet |

### Typography
- **Body/Heading:** Geist Variable (loaded via `@fontsource-variable/geist`)
- **Mono:** JetBrains Mono (CSS var only — system fallback)

### Motion (`src/lib/motion.ts`)
- `springTransition` — spring(400, 32)
- `dashboardGridVariants`, `dashboardCardVariants`, `dialogVariants`, `panelVariants`, `commandPaletteItemVariants`

### Design System Rules
1. No second design system — use existing tokens only
2. No new CSS variables unless a new theme token is truly needed
3. Extend, do not replace — `bg-card`, `border-border`, `text-muted-foreground`
4. Motion — use existing variants from `lib/motion.ts`
5. Icons — `lucide-react` only; no MUI/Ant Design/Chakra

---

## 17. Mobile Responsive Audit

| Width | Sidebar | Inspector | Notes |
|---|---|---|---|
| <768px | Off-screen, hamburger | Hidden | Full-width content |
| 768–1023px | Icon-only (68px) | Overlay, auto-closes | Reduced width |
| 1024–1279px | Auto-collapses on mount | Overlay | Standard layout |
| ≥1280px | Expanded (260px) | Inline right | Full 3-column |

**Currently responsive:** Sidebar animation, hamburger, backdrop overlay, search truncation.

**Currently NOT responsive:**
- `EmailPage` — `w-96` left pane is fixed, no mobile treatment
- `WorkspacePage` — 2-pane may squeeze on mobile
- Developer studio pages — desktop-only

**R1/R2 mobile requirement:** EmailPage must collapse to single-pane on <768px. Developer studios may remain desktop-only.

---

## 18. Final Target Information Architecture

```
ROUTE                                    COMPONENT
/auth                                    AuthPage (unchanged)
/                                        Home — real data only
                                           Email: urgent items from /api/v1/email/digest
                                           Conversations: recent from /conversations
                                           Quick actions: New chat, Upload, Open Email
/assistant                               WorkspacePage (same component, renamed route)
/email                                   EmailPage (unchanged)
/files                                   FilesPage (rewired to real API)
/settings                                SettingsPage (expanded)
  /settings/account                      Profile (NEW)
  /settings/appearance                   Theme + density
  /settings/memory                       Memory controls
  /settings/developer                    Developer / AIOS portal
    /settings/developer/overview         System health
    /settings/developer/agents           AgentsPage (REUSE)
    /settings/developer/tools            ToolsPage (REUSE)
    /settings/developer/workflows        WorkflowPage (REUSE)
    /settings/developer/memory           MemoryPage (REUSE)
    /settings/developer/rag              RAGPage (REUSE)
    /settings/developer/models           ModelsPage (REUSE)
    /settings/developer/prompts          PromptsPage (REUSE)
    /settings/developer/integrations/mcp NEW
    /settings/developer/integrations/connections NEW (Gmail OAuth)
    /settings/developer/deployment       DeploymentPage (REUSE)
    /settings/developer/observability    NEW wrapper

SIDEBAR (5 items only):
  Home | Assistant | Email | Files | Settings
```

---

## 19. Route Redirect Map

Implement all redirects in R1 via `<Route path="…" element={<Navigate to="…" replace />} />` inside `App.tsx`.

| Old Route | New Route | Risk | Component |
|---|---|---|---|
| `/dashboard` | `/` | MEDIUM (bookmarks) | DashboardPage widgets reused |
| `/workspace` | `/assistant` | HIGH (bookmarks) | WorkspacePage (exact) |
| `/agents` | `/settings/developer/agents` | MEDIUM | AgentsPage (exact) |
| `/memory` | `/settings/developer/memory` | MEDIUM | MemoryPage (exact) |
| `/tools` | `/settings/developer/tools` | LOW | ToolsPage (exact) |
| `/rag` | `/settings/developer/rag` | LOW | RAGPage (exact) |
| `/models` | `/settings/developer/models` | LOW | ModelsPage (exact) |
| `/workflows` | `/settings/developer/workflows` | LOW | WorkflowPage (exact) |
| `/deployments` | `/settings/developer/deployment` | LOW | DeploymentPage (exact) |
| `/prompts` | `/settings/developer/prompts` | LOW | PromptsPage (exact) |

No redirects needed for: `/`, `/files`, `/email`, `/settings`, `/auth`.

---

## 20. Capability Preservation Matrix

| Capability | Current | Target | Backend | Action |
|---|---|---|---|---|
| Chat / Assistant | `/workspace` | `/assistant` | YES (SSE + conversations) | Restyle |
| Email | `/email` | `/email` | YES (full pipeline) | Polish |
| Auth | `/auth` | `/auth` | YES | Keep |
| Files Upload | `/files` | `/files` | YES | Wire to real API |
| Agents Studio | `/agents` | `/settings/developer/agents` | YES | Relocate |
| Memory Studio | `/memory` | `/settings/developer/memory` | YES | Relocate |
| Tools Studio | `/tools` | `/settings/developer/tools` | YES | Relocate |
| RAG Studio | `/rag` | `/settings/developer/rag` | YES | Relocate |
| Model Studio | `/models` | `/settings/developer/models` | YES | Relocate |
| Workflow Studio | `/workflows` | `/settings/developer/workflows` | YES | Relocate |
| Deployment Studio | `/deployments` | `/settings/developer/deployment` | YES | Relocate |
| Prompt Studio | `/prompts` | `/settings/developer/prompts` | YES | Relocate |
| MCP Manager | inside /tools | `/settings/developer/integrations/mcp` | YES | New page |
| Observability | no page | `/settings/developer/observability` | YES | New page |
| Theme switching | `/settings` | `/settings/appearance` | N/A (local) | Keep |
| Command Palette | ⌘K | ⌘K | N/A | Update commands |
| Inspector Panel | ⌘I | ⌘I simplified | N/A | Simplify |

---

## 21. Mock Data Register (21 items)

Must be replaced with real data or honest empty states before final release. Do NOT remove during R0 or R1.

| # | File | What's Fake | Future Replacement |
|---|---|---|---|
| 1 | `Hero.tsx` L9 | `userName = "Virat"` | `useAuthStore().user.email` split |
| 2 | `ContinueWorking.tsx` L20–57 | 4 workspace cards | Recent conversations from `/conversations` |
| 3 | `Projects.tsx` L20–65 | 4 project cards | REMOVE — no backend planned |
| 4 | `Agents.tsx` L25–88 | 6 agent cards | Query `/agents` endpoint or remove from Home |
| 5 | `Conversations.tsx` L23–51 | 3 conversations | Wire `useConversationsQuery()` |
| 6 | `SystemHealth.tsx` L20–87 | 6 subsystems all nominal | REMOVE from Home; move to Developer/Overview |
| 7 | `Notifications.tsx` L15–44 | 4 notifications | Wire to email digest or remove |
| 8 | `Timeline.tsx` L14–50 | 5 timeline events | Wire to agent executions or remove |
| 9 | `Insights.tsx` L8–21 | Model usage, vector count | Move to Developer/Overview; remove from Home |
| 10 | `FilesPage.tsx` L7–11 | 3 hardcoded files | Wire to `/files` + RAG dataset list |
| 11 | `FilesPage.tsx` L33,43,53 | "14 Files", "842 Chunks", "98% Sync" | Compute from real API |
| 12 | `AppShell.tsx` L105–111 | 5 workspace items | REMOVE — replace with user profile dropdown |
| 13 | `AppShell.tsx` L566 | "1.2GB" DB size | Wire to `/health` or remove |
| 14 | `AppShell.tsx` L570 | "Tokens: 1.4k" | Wire from SSE streaming context or remove |
| 15 | `InspectorPanel.tsx` Context | Session ID, token counts | Wire from WorkspacePage state in R2 |
| 16 | `InspectorPanel.tsx` Memory | 1,824 vectors, memory keys | Wire from memory API or remove |
| 17 | `InspectorPanel.tsx` Thoughts | 3 reasoning steps | Wire to `agent_state` SSE events in R2 |
| 18 | `InspectorPanel.tsx` Files | 4 listed files | Wire to session attachments in R2 |
| 19 | `InspectorPanel.tsx` Tool Output | `read_directory()` result | Wire to `tool_output` SSE events in R2 |
| 20 | `InspectorPanel.tsx` Debugger | Heap, latency metrics | Wire to `/health` or remove |
| 21 | `InspectorPanel.tsx` Email | PLACEMENT, score 95 | Wire to selected email state in R2 |

---

## 22. Dead UI Register (17 items)

| # | File | Element | Why Dead | Action |
|---|---|---|---|---|
| 1 | `CommandPalette.tsx` | "Sync Vector Database" ⌘S | `console.log(...)` | Remove or wire in R3 |
| 2 | `CommandPalette.tsx` | "Start Code Orchestrator" | `console.log(...)` | Remove in R3 |
| 3 | `CommandPalette.tsx` | "Restart AIOS Kernel" | `console.log(...)` | Remove in R3 |
| 4 | `CommandPalette.tsx` | "Toggle Left Sidebar" ⌘B | `console.log(...)` | Wire properly or remove in R3 |
| 5 | `CommandPalette.tsx` | "Find in Files" ⌘F | `console.log(...)` | Wire to SearchModal in R3 |
| 6 | `AppShell.tsx` | Workspace switcher (5 items) | No backend, no purpose | Remove in R1 |
| 7 | `AppShell.tsx` | Bell notification button | No onClick, no notification system | Remove or wire in R1 |
| 8 | `AppShell.tsx` | "CONNECTED" pill | Always shows regardless of connectivity | Wire to `/health` or remove in R1 |
| 9 | `SettingsPage.tsx` | General AI Engine form inputs | No save handler | Wire or remove in R2 |
| 10 | `SettingsPage.tsx` | Security Settings form inputs | No save handler | Wire or remove in R2 |
| 11 | `SettingsPage.tsx` | Cancel / Save buttons | No handlers | Wire in R2 |
| 12 | `FilesPage.tsx` | "Add Document" button | No onClick / no upload dialog | Wire to file upload in R2 |
| 13 | `App.tsx` routes | `/rag`, `/workflows`, `/deployments`, `/prompts` | No sidebar entry — unreachable | Add to Developer nav in R1 |
| 14 | `AppShell.tsx` | "Profile Details" user menu item | No route or action | Wire to `/settings/account` in R1 |
| 15 | `AppShell.tsx` | "Preference Settings" user menu item | No route or action | Wire to `/settings` in R1 |
| 16 | `InspectorPanel.tsx` | Resize handle (left border `w-px`) | Visual only, not draggable | Implement or remove in R2 |
| 17 | `AppShell.tsx` | Commented Travel Planner, Jobs & Internships nav items | Commented out | Remove commented code in R3 |

---

## 23. Deferred Features

Must NOT be built during R1/R2/R3:

| Feature | Reason |
|---|---|
| Continuous Gmail monitoring | No background worker/scheduler in current stack |
| Gmail send / reply | Read-only OAuth scope — by design |
| Gmail delete / label management | Out of Email Prompt 1–3 scope |
| Jobs Agent | Not started |
| Travel Agent | Not started (commented in AppShell) |
| Codebase Intelligence | Not implemented |
| Notification event bus | No backend event system |
| Redis / Celery background jobs | No Redis in current stack |
| Account settings save backend | No `/settings` CRUD API |
| Notification preferences backend | No notification backend |
| Privacy / data retention backend | No retention API |
| File rename / delete | Files page is upload + read only |
| Multi-region infrastructure | Out of scope |
| Enterprise governance / RBAC | Out of scope |
| Real-time collaboration | Out of scope |
| Push notifications | No backend push system |
| Auto-reply drafting | Not implemented in backend |

---

## 24. Redesign Invariants (12 — ABSOLUTE)

1. **Backend Preservation** — No redesign prompt may touch backend files.
2. **Authentication Preservation** — `auth.ts`, `authStore.ts`, `apiClient.ts`, `providers/index.tsx`, `App.tsx` auth wrappers must not be modified unless narrowly justified.
3. **SSE Preservation** — `services/api/sse.ts` and streaming state machine in `WorkspacePage.tsx` must not be modified in R1. R2 may add display only.
4. **API Contract Preservation** — Existing endpoint paths, methods, and schemas remain unchanged. No API change required by the redesign.
5. **Real Data Only** — No new hardcoded fake production data. Where real data is unavailable: honest empty state, loading skeleton, or connection prompt.
6. **Move, Don't Destroy** — Working developer capabilities are relocated, not deleted. Existing page components must be reused.
7. **Reuse First** — Check for existing component before creating a new one. Use existing shadcn library, motion variants, layout patterns.
8. **URL Continuity** — Every current meaningful URL must redirect to its new location via `<Navigate replace>`. No old URL may 404.
9. **No Technical Jargon in Normal UX** — Terms: LangGraph, ToolEngine, MCP, RAG, embeddings, vector store, chunking, supervisor, AIOS kernel — never in Home/Assistant/Email/Files UI. Acceptable only in Developer / AIOS.
10. **Human Approval** — Consequential external actions (send email, delete files, terminal commands) remain gated by existing backend security. Redesign must not add bypass paths.
11. **No Scope Expansion** — R1/R2/R3 must not begin implementing any feature listed in §23.
12. **Honest Capability Reporting** — If Gmail is not connected, show connect prompt — not a fake inbox. If no emails synced, show honest empty state.

---

## 25. R1/R2/R3 Implementation Constraints

### R1 — App Shell + Home + Settings + Developer / AIOS

**Allowed to MODIFY:**
- `frontend/src/App.tsx` — routes, redirects, new sub-routes under `/settings/developer/*`
- `frontend/src/components/layout/AppShell.tsx` — 5-item sidebar, remove workspace switcher
- `frontend/src/components/common/CommandPalette.tsx` — update command list
- `frontend/src/components/layout/InspectorPanel.tsx` — simplify tabs
- `frontend/src/features/Dashboard/DashboardPage.tsx` — restyle as Home attention center
- `frontend/src/features/Dashboard/widgets/*.tsx` — real-data versions
- `frontend/src/features/Settings/SettingsPage.tsx` — expand with new sections

**Allowed to CREATE:**
- New sub-pages under `frontend/src/features/Settings/`
- Developer portal landing page + subpages
- Redirect wrapper elements

**Must NOT touch:**
- `features/Workspace/WorkspacePage.tsx` and all sub-components
- `features/Email/` — all files
- `features/Files/FilesPage.tsx` — deferred to R2
- All developer studio pages (only add new routes in App.tsx pointing to them)
- `services/api/sse.ts`, `services/store/authStore.ts`, `services/api/auth.ts`, `services/api/apiClient.ts`
- Any backend file

**R1 regression verification:**
- Backend pytest: 347 passed (baseline)
- Ruff: All checks passed
- Pyright: ≤101 errors (no new)
- Frontend lint: 0 errors
- Frontend build: passes
- Auth: login → home → logout works
- `/workspace` or `/assistant`: chat still works
- `/email`: still loads and queries work

---

### R2 — Assistant + Email + Files

**Allowed to MODIFY:**
- `features/Workspace/WorkspacePage.tsx` — visual only; SSE logic must not change
- `features/Workspace/components/*.tsx` — polish, mobile layout improvements
- `features/Email/EmailPage.tsx` — mobile single-pane, polish
- `features/Email/InboxList.tsx`, `EmailDetail.tsx`, `DigestView.tsx`, `SenderAuthBadge.tsx` — visual improvements
- `features/Files/FilesPage.tsx` — wire to real API, remove mocked data, add upload UX
- `components/layout/InspectorPanel.tsx` — wire AI Thoughts to SSE events, wire Email tab to selected email

**May CREATE:**
- Email mobile layout sub-components
- File upload dialog component

**Must NOT touch:**
- R1 routing changes in App.tsx
- R1 AppShell nav changes
- Backend API contracts
- `services/api/sse.ts`
- Auth services

---

### R3 — Cleanup + Final Verification

**Allowed to MODIFY / DELETE:**
- Remove dead command palette entries (sys-sync, sys-start, sys-kernel, cmd-sidebar, cmd-search)
- Fix shortcut collisions in CommandPalette
- Remove hardcoded mock data; replace with empty states or real data hooks
- Remove workspace switcher dead code from AppShell
- Remove commented-out Travel Planner, Jobs nav items
- Remove AppShell status bar hardcoded strings
- Remove FilesPage hardcoded file entries (now wired from R2)
- Wire or remove Settings form inputs
- Update documentation

**Must NOT touch:** Any backend file, auth, SSE, email backend integration, API contracts.

---

## 26. Baseline Regression Table

Captured 2026-09-27 at R0 audit time:

| Check | Baseline |
|---|---|
| Backend pytest | **347 passed, 1 warning in 9.22s** |
| Ruff | **All checks passed!** |
| Pyright | **101 errors, 6 warnings** (all pre-existing in legacy test suites — `test_Tools/`, `test_LangGraph/`) |
| Frontend lint (oxlint) | **0 warnings and 0 errors. 176 files** |
| Frontend build | **✓ built in 449ms** |
| Git branch | **main** |
| Git HEAD | **1927420** |

---

## R0 Self-Review — 21/21 PASS

| # | Question | Answer |
|---|---|---|
| 1 | Modified only `docs/IA_LOCK.md`? | YES |
| 2 | Source files accidentally modified? | NO |
| 3 | Inspected actual routes from `App.tsx`? | YES — 15 routes documented |
| 4 | Inspected actual components? | YES — AppShell, InspectorPanel, CommandPalette, all features |
| 5 | Inspected Email after Prompt 3? | YES — all 7 email files read |
| 6 | Distinguished real vs mocked data? | YES — 21-item register §21 |
| 7 | Preserved backend dependencies? | YES — §7 |
| 8 | Documented authentication? | YES — §8 with critical files |
| 9 | Documented SSE? | YES — §8 with implementation details |
| 10 | Documented developer surfaces? | YES — §12, 10 surfaces |
| 11 | Documented route redirects? | YES — §19 |
| 12 | Identified fake production data? | YES — 21 items |
| 13 | Identified dead UI? | YES — 17 items |
| 14 | Identified reusable components? | YES — §5, §20 |
| 15 | Avoided inventing unsupported functionality? | YES — §23 deferred list |
| 16 | Preserved 5-item primary navigation? | YES — §1, §18 |
| 17 | Preserved Developer / AIOS? | YES — §12, §18 |
| 18 | Defined R1/R2/R3 boundaries? | YES — §25 |
| 19 | Another engineer can execute from this document? | YES |
| 20 | Invariants prevent redesign drift? | YES — §24 (12 invariants) |
| 21 | Ran any SQL or DB command? | NO — database not touched |

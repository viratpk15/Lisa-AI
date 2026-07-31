# Jarvis AIOS Placement Edition v1.0

[![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)](docs/RELEASE_NOTES_v1.0.md)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](docs/RELEASE_READINESS.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](docs/LICENSE_NOTICE.md)

**Jarvis AIOS** is a production-grade AI Operating System designed for extensibility, maintainability, security, and multi-cloud deployment.

It unifies autonomous agent orchestration, RAG retrieval, prompt engineering, dynamic LLM model routing, visual workflow graph building, and multi-cluster deployment under a single integrated platform.

---

## 🏛️ Architecture Overview

Jarvis AIOS follows a strict 7-layer decoupled architecture:

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

## 🚀 Quickstart Guide

### Prerequisites
- **Python:** 3.12+ (managed via `uv`)
- **Node.js:** 18+ or 20+ (managed via `pnpm`)
- **Docker:** Version 24.0+ (optional, for containerized run)

### 1. Backend Setup
```bash
cd backend
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
pnpm install
pnpm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🧪 Verification Commands

Execute the automated verification suite:

```bash
# Backend Verification
cd backend
uv run pytest
uv run ruff check .

# Frontend Verification
cd frontend
pnpm run lint
pnpm run build
```

---

## 📚 Documentation Index

- [Release Notes v1.0](docs/RELEASE_NOTES_v1.0.md)
- [Changelog](docs/CHANGELOG.md)
- [Installation Guide](docs/INSTALLATION_GUIDE.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md)
- [Platform Integration Report](docs/PLATFORM_INTEGRATION_REPORT.md)
- [Production Hardening Report](docs/PRODUCTION_HARDENING_REPORT.md)
- [Performance Optimization Report](docs/PERFORMANCE_REPORT.md)
- [Security Audit Report](docs/SECURITY_AUDIT.md)
- [Measured Release Readiness Assessment](docs/RELEASE_READINESS.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)
- [License Notice](docs/LICENSE_NOTICE.md)
- [Known Limitations](docs/KNOWN_LIMITATIONS.md)
- [Roadmap v2.0](docs/ROADMAP_v2.md)

---

## 📄 License

Distributed under the MIT License. See [LICENSE_NOTICE.md](docs/LICENSE_NOTICE.md) for details.

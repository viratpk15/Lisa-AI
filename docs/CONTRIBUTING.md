# Contributing Guidelines — Jarvis AIOS

Thank you for contributing to Jarvis AIOS Placement Edition! To maintain production quality and architectural integrity, please adhere to these guidelines.

---

## 1. Engineering Constitution & Rules

Before contributing code:
1. Read `docs/ARCHITECTURE_OVERVIEW.md` and `docs/03_CODING_STANDARDS.md`.
2. Maintain strict 7-layer decoupling:
   `FastAPI -> Runtime -> LangGraph -> Tool Engine -> Tool Registry -> Tools -> LLM`.
3. Never bypass layers or import FastAPI routes directly into LangGraph graph nodes.
4. All database models must inherit from `Base` in `app.Data.base`.

---

## 2. Development Workflow

1. **Fork & Branch:** Create a feature branch off `feature/placement-edition`:
   ```bash
   git checkout -b feature/my-feature-name
   ```

2. **Backend Development:**
   - Add unit tests in `backend/app/tests/`.
   - Run tests: `cd backend && uv run pytest`
   - Check linting: `cd backend && uv run ruff check .`

3. **Frontend Development:**
   - Place components in appropriate `frontend/src/features/<Studio>/` directory.
   - Run linter: `cd frontend && pnpm run lint`
   - Run production build: `cd frontend && pnpm run build`

4. **Commit & Push:** Write descriptive commit messages using conventional commit format:
   `feat(subsystem): short description` or `fix(subsystem): short description`.

---

## 3. Pull Request Review Criteria

All PRs require:
- 100% passing backend unit & integration tests.
- 0 `ruff` lint errors.
- 0 `oxlint` frontend lint errors.
- Clean Vite production build.

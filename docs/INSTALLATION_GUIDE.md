# Installation Guide — Jarvis AIOS v1.0

Follow this guide to set up a local development environment for Jarvis AIOS.

---

## 1. System Requirements

- **Operating System:** macOS, Linux, or Windows (WSL2 recommended)
- **Python:** 3.12+ (managed via `uv`)
- **Node.js:** 18+ or 20+
- **Package Managers:** `uv` for Python, `pnpm` for Node.js

---

## 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

3. Configure local environment variables:
   ```bash
   cp .env.example .env
   ```

4. Run database migrations:
   ```bash
   uv run alembic upgrade head
   ```

5. Start the FastAPI development server:
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

6. Run backend unit tests:
   ```bash
   uv run pytest
   ```

---

## 3. Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies via `pnpm`:
   ```bash
   pnpm install
   ```

3. Start the Vite development server:
   ```bash
   pnpm run dev
   ```
   The UI will be accessible at `http://localhost:5173`.

4. Run frontend linters and build checks:
   ```bash
   pnpm run lint
   pnpm run build
   ```

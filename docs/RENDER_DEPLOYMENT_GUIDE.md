# Render + Supabase Deployment Guide — Jarvis AIOS v1.0

This guide provides step-by-step instructions for deploying Jarvis AIOS Placement Edition to **Render** (Free Tier) using **Supabase PostgreSQL** (Free Tier) as the production database.

---

## 1. Architecture & Deployment Strategy

- **Backend Web Service:** Render Web Service (Python 3.12, FastAPI, Uvicorn).
- **Frontend Web Service:** Render Static Site (Vite Single Page App).
- **Production Database:** Supabase Managed PostgreSQL.
- **Cost:** **$0.00 / month** (100% Free Tier compatible).

---

## 2. Supabase Setup (PostgreSQL Database)

1. Create a free account at [Supabase.com](https://supabase.com).
2. Create a new project named `Jarvis-AIOS-Prod`.
3. In your Supabase Dashboard, navigate to **Project Settings -> Database -> Connection String**.
4. Copy the URI string under **Transaction / Direct Connection**:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```

---

## 3. Render Backend Deployment

1. Sign up / log in to [Render.com](https://render.com).
2. Click **New + -> Web Service**.
3. Connect your GitHub repository (`Jarvis-Virat-AIOS`).
4. Configure service settings:
   - **Name:** `jarvis-aios-backend`
   - **Region:** Oregon (US West) or closest region
   - **Branch:** `feature/placement-edition` (or `main`)
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install uv && uv sync`
   - **Start Command:** `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`

5. Add Environment Variables in Render:
   | Key | Value | Notes |
   | :--- | :--- | :--- |
   | `DATABASE_PROVIDER` | `postgres` | Instructs engine to use PostgreSQL |
   | `DATABASE_URL` | `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres` | Supabase URI |
   | `JWT_SECRET_KEY` | `<your-secure-random-32-byte-secret>` | Secret for signing JWT access tokens |
   | `JWT_ALGORITHM` | `HS256` | Token signing algorithm |
   | `CORS_ORIGINS` | `https://jarvis-aios-frontend.onrender.com` | Production Frontend URL |
   | `OPENAI_API_KEY` | `sk-...` | Optional default LLM key |

---

## 4. Render Frontend Deployment

1. In Render Dashboard, click **New + -> Static Site**.
2. Connect your GitHub repository (`Jarvis-Virat-AIOS`).
3. Configure static site settings:
   - **Name:** `jarvis-aios-frontend`
   - **Branch:** `feature/placement-edition`
   - **Root Directory:** `frontend`
   - **Build Command:** `pnpm install && pnpm run build`
   - **Publish Directory:** `dist`

4. Add Rewrite Rule (for Single Page Application routing):
   - **Source:** `/*`
   - **Destination:** `/index.html`
   - **Action:** Rewrite

---

## 5. Post-Deployment Verification Checklist

1. **Alembic Migration Execution:**
   Run initial migration from your local terminal targeting Supabase:
   ```bash
   DATABASE_PROVIDER=postgres DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres" uv run alembic upgrade head
   ```

2. **Backend API Docs:**
   Navigate to `https://jarvis-aios-backend.onrender.com/docs`.

3. **Cluster Health Check:**
   Navigate to `https://jarvis-aios-backend.onrender.com/api/v1/deployments/prod/health`.
   Verify response:
   ```json
   {
     "status": "connected",
     "provider": "postgres",
     "version": "PostgreSQL 15.x ... on Supabase"
   }
   ```

4. **Frontend UI Walkthrough:**
   Open `https://jarvis-aios-frontend.onrender.com` and test all 8 Studios.

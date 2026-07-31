# Deployment Guide — Jarvis AIOS v1.0

This guide details how to deploy Jarvis AIOS Placement Edition to production using Docker Compose, Kubernetes Helm, or PaaS providers.

---

## 1. Prerequisites

- **Docker:** Version 24.0+ and Docker Compose v2.20+
- **Kubernetes (Optional):** Cluster v1.26+ and `kubectl` CLI
- **Node.js & Python:** Node.js v18+ & Python 3.12+ (for bare-metal or local dev)

---

## 2. Docker Compose Deployment (Recommended)

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/viratpk15/Jarvis-Virat-AIOS.git
   cd Jarvis-Virat-AIOS
   ```

2. **Configure Environment Variables:**
   Copy `.env.example` to `backend/.env`:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Configure mandatory keys:
   ```ini
   SECRET_KEY=your_secure_random_jwt_secret
   DATABASE_URL=sqlite:///./jarvis.db
   OPENAI_API_KEY=sk-...
   ```

3. **Build & Launch Containers:**
   ```bash
   docker-compose up -d --build
   ```

4. **Verify Deployment Health:**
   - **Frontend UI:** `http://localhost:5173`
   - **Backend API Docs:** `http://localhost:8000/docs`
   - **Health Endpoint:** `http://localhost:8000/api/v1/deployments/prod/health`

---

## 3. Kubernetes Deployment

Manifest templates are available via Deployment Studio or inside `.private/docs/deployment-studio/`:

1. **Apply ConfigMaps & Secrets:**
   ```bash
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secret.yaml
   ```

2. **Deploy Application Pods:**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

---

## 4. Disaster Recovery & Database Backups

- **Create Manual Snapshot:**
  In Deployment Studio UI or via API:
  `POST /api/v1/deployments/backups`
- **Restore Snapshot:**
  `POST /api/v1/deployments/backups/restore` with snapshot name.

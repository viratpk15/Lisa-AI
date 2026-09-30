# Jarvis AIOS — LLM Provider Strategy & Architecture

## 1. Locked LLM Provider Policy

Jarvis AIOS enforces a strict, deterministic multi-provider failover strategy across environments:

### Development Environment (`ENVIRONMENT=development`)
Failover Order:
1. **Groq Cloud** (`llama-3.3-70b-versatile`) — Primary low-latency cloud inference
2. **NVIDIA NIM** (`meta/llama-3.3-70b-instruct`) — Secondary cloud inference fallback
3. **Mistral AI** (`mistral-large-latest`) — Tertiary cloud inference fallback
4. **Ollama Local** (`qwen2.5:3b`) — Offline development-only local fallback

### Production Environment (`ENVIRONMENT=production`)
Failover Order:
1. **Groq Cloud** (`llama-3.3-70b-versatile`) — Primary production inference
2. **NVIDIA NIM** (`meta/llama-3.3-70b-instruct`) — Secondary production fallback
3. **Mistral AI** (`mistral-large-latest`) — Tertiary production fallback

> **CRITICAL POLICY CONSTRAINT**: Ollama MUST NEVER be a production fallback. If all three production cloud providers (Groq, NVIDIA NIM, Mistral) are unavailable in production, the system raises a recoverable provider error and terminates rather than routing traffic to local Ollama.

---

## 2. User-Facing Models UI

The normal user-facing Model Studio interfaces (Model Registry, Providers, Latency Benchmark, Cost Calculator) display only authorized inference providers:
* **Visible**: Groq, NVIDIA NIM, Mistral
* **Hidden from Normal UX**: Ollama (development-only fallback), Gemini, Anthropic, OpenRouter, Cerebras, Together, Fireworks

---

## 3. Pre-Token Failover & Mid-Stream Safety

* **Pre-Token Failover**: If a provider fails due to rate limits (HTTP 429), server errors (500/503), timeouts, or missing credentials before any tokens are emitted, the stateless `LLMRouter` catches `RecoverableLLMError` and immediately routes the request to the next provider in the chain.
* **Mid-Stream Safety**: If a failure occurs after tokens have already been streamed to the user, splicing tokens from another provider is strictly aborted to prevent content corruption and hallucinated context mismatches.

---

## 4. Environment Configuration

| Variable | Environment | Default / Example | Purpose |
|---|---|---|---|
| `ENVIRONMENT` | All | `development` / `production` | Enforces production vs development failover chain |
| `GROQ_API_KEY` | All | `gsk_...` | Groq platform API key |
| `GROQ_MODEL` | All | `llama-3.3-70b-versatile` | Groq model identifier |
| `NVIDIA_API_KEY` | All | `nvapi-...` | NVIDIA NIM platform API key |
| `NVIDIA_MODEL` | All | `meta/llama-3.3-70b-instruct` | NVIDIA NIM model identifier |
| `NVIDIA_BASE_URL` | All | `https://integrate.api.nvidia.com/v1` | NVIDIA NIM OpenAI-compatible endpoint |
| `MISTRAL_API_KEY` | All | `...` | Mistral AI platform API key |
| `MISTRAL_MODEL` | All | `mistral-large-latest` | Mistral model identifier |
| `MISTRAL_BASE_URL` | All | `https://api.mistral.ai/v1` | Mistral OpenAI-compatible endpoint |
| `OLLAMA_BASE_URL` | Dev Only | `http://localhost:11434` | Local Ollama endpoint (Dev fallback only) |
| `OLLAMA_MODEL` | Dev Only | `qwen2.5:3b` | Local Ollama model identifier |

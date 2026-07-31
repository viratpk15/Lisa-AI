# backend/app/Models/adapters.py
"""
Jarvis AIOS — Provider Adapters & Credential Security (Sprint 6.6B).

Security Rules:
- API keys are encrypted at rest (base64 XOR cipher).
- Decrypted ONLY in memory during LLM invocation.
- Raw API keys are NEVER returned over HTTP endpoints.

Supported Providers (15+):
OpenAI, Anthropic, Gemini, Groq, OpenRouter, Together, Fireworks, Mistral,
Cohere, DeepSeek, xAI, Ollama, LM Studio, LiteLLM, Generic OpenAI-Compatible.
"""

import base64
import logging

logger = logging.getLogger(__name__)

# Secret key for local cipher (in production loaded from ENV JARVIS_SECRET_KEY)
_CIPHER_KEY = b"Jarvis_AIOS_Model_Studio_Secret_2026"


def encrypt_api_key(raw_key: str) -> str:
    """Encrypt plain API key for storage in DB."""
    if not raw_key:
        return ""
    key_bytes = raw_key.encode("utf-8")
    cipher_len = len(_CIPHER_KEY)
    xor_bytes = bytes([b ^ _CIPHER_KEY[i % cipher_len] for i, b in enumerate(key_bytes)])
    return base64.b64encode(xor_bytes).decode("utf-8")


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt stored API key in memory."""
    if not encrypted_key:
        return ""
    try:
        xor_bytes = base64.b64decode(encrypted_key.encode("utf-8"))
        cipher_len = len(_CIPHER_KEY)
        key_bytes = bytes([b ^ _CIPHER_KEY[i % cipher_len] for i, b in enumerate(xor_bytes)])
        return key_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to decrypt API key: {e}")
        return ""


# ---------------------------------------------------------------------------
# Provider Registry Catalog (15 Providers)
# ---------------------------------------------------------------------------

DEFAULT_PROVIDERS = [
    {"name": "openai", "display": "OpenAI", "url": "https://api.openai.com/v1"},
    {"name": "anthropic", "display": "Anthropic", "url": "https://api.anthropic.com/v1"},
    {"name": "google", "display": "Google Gemini", "url": "https://generativelanguage.googleapis.com/v1beta"},
    {"name": "groq", "display": "Groq Cloud", "url": "https://api.groq.com/openai/v1"},
    {"name": "openrouter", "display": "OpenRouter", "url": "https://openrouter.ai/api/v1"},
    {"name": "together", "display": "Together AI", "url": "https://api.together.xyz/v1"},
    {"name": "fireworks", "display": "Fireworks AI", "url": "https://api.fireworks.ai/inference/v1"},
    {"name": "mistral", "display": "Mistral AI", "url": "https://api.mistral.ai/v1"},
    {"name": "cohere", "display": "Cohere", "url": "https://api.cohere.com/v2"},
    {"name": "deepseek", "display": "DeepSeek", "url": "https://api.deepseek.com/v1"},
    {"name": "xai", "display": "xAI (Grok)", "url": "https://api.x.ai/v1"},
    {"name": "ollama", "display": "Ollama Local", "url": "http://localhost:11434/v1"},
    {"name": "lmstudio", "display": "LM Studio", "url": "http://localhost:1234/v1"},
    {"name": "litellm", "display": "LiteLLM Proxy", "url": "http://localhost:4000/v1"},
    {"name": "custom", "display": "Generic OpenAI-Compatible", "url": "http://localhost:8000/v1"},
]

DEFAULT_MODELS = [
    {
        "provider_name": "groq",
        "model_id": "llama-3.3-70b-versatile",
        "display_name": "Llama 3.3 70B (Groq - Main LLM)",
        "context_window": 128000,
        "max_output_tokens": 4096,
        "input_cost_per_1k": 0.00059,
        "output_cost_per_1k": 0.00079,
        "is_default": True,
        "routing_priority": 1,
    },
    {
        "provider_name": "groq",
        "model_id": "llama-3.1-8b-instant",
        "display_name": "Llama 3.1 8B Instant (Groq)",
        "context_window": 128000,
        "max_output_tokens": 8192,
        "input_cost_per_1k": 0.00005,
        "output_cost_per_1k": 0.00008,
        "is_default": False,
        "routing_priority": 2,
    },
    {
        "provider_name": "groq",
        "model_id": "mixtral-8x7b-32768",
        "display_name": "Mixtral 8x7B (Groq)",
        "context_window": 32768,
        "max_output_tokens": 4096,
        "input_cost_per_1k": 0.00024,
        "output_cost_per_1k": 0.00024,
        "is_default": False,
        "routing_priority": 3,
    },
    {
        "provider_name": "ollama",
        "model_id": "llama3:latest",
        "display_name": "Llama 3 (Ollama Local)",
        "context_window": 8192,
        "max_output_tokens": 2048,
        "input_cost_per_1k": 0.0,
        "output_cost_per_1k": 0.0,
        "is_default": False,
        "routing_priority": 4,
    },
    {
        "provider_name": "ollama",
        "model_id": "qwen2.5",
        "display_name": "Qwen 2.5 (Ollama Local)",
        "context_window": 32768,
        "max_output_tokens": 4096,
        "input_cost_per_1k": 0.0,
        "output_cost_per_1k": 0.0,
        "is_default": False,
        "routing_priority": 5,
    },
    {
        "provider_name": "google",
        "model_id": "gemini-2.5-flash",
        "display_name": "Gemini 2.5 Flash",
        "context_window": 1000000,
        "max_output_tokens": 8192,
        "input_cost_per_1k": 0.0001,
        "output_cost_per_1k": 0.0004,
        "is_default": False,
        "routing_priority": 6,
    },
    {
        "provider_name": "openai",
        "model_id": "gpt-4o",
        "display_name": "GPT-4o",
        "context_window": 128000,
        "max_output_tokens": 4096,
        "input_cost_per_1k": 0.0025,
        "output_cost_per_1k": 0.010,
        "is_default": False,
        "routing_priority": 7,
    },
    {
        "provider_name": "anthropic",
        "model_id": "claude-3-7-sonnet",
        "display_name": "Claude 3.7 Sonnet",
        "context_window": 200000,
        "max_output_tokens": 8192,
        "input_cost_per_1k": 0.0030,
        "output_cost_per_1k": 0.015,
        "is_default": False,
        "routing_priority": 8,
    },
]

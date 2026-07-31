"""
Jarvis AIOS
--------------------
Central LLM Client

Exposes a provider-independent LLM client abstraction shielding higher-level
modules (Runtime, LangGraph) from provider-specific SDKs (Groq, OpenAI, Gemini, etc.).
"""

from typing import Any, Generator
from dotenv import load_dotenv

load_dotenv()


from app.LLM.router import llm_router


class LLMClient:
    """Provider-independent LLM client interface backed by production LLMRouter."""

    def __init__(self, provider: Any = None, provider_type: str = "groq", model: str = "llama-3.3-70b-versatile") -> None:
        self._custom_provider = provider
        self.provider_type = provider_type
        self.model = model

    @property
    def provider(self) -> Any:
        """Get underlying router object for LangChain compatibility."""
        return self

    def invoke(self, input_data: Any, **kwargs: Any) -> Any:
        """Synchronously invoke LLM via stateless router with recoverable failover."""
        if self._custom_provider:
            return self._custom_provider.invoke(input_data, **kwargs)

        messages = input_data if isinstance(input_data, list) else [input_data]
        return llm_router.invoke(messages, **kwargs)

    def stream(self, input_data: Any, **kwargs: Any) -> Generator[str, None, None]:
        """Stream token strings via stateless router with pre-token failover and mid-stream safety."""
        if self._custom_provider and hasattr(self._custom_provider, "stream"):
            for chunk in self._custom_provider.stream(input_data, **kwargs):
                token = getattr(chunk, "content", None) or str(chunk)
                if token:
                    yield token
            return

        messages = input_data if isinstance(input_data, list) else [input_data]
        yield from llm_router.stream(messages, **kwargs)


def get_llm_client(provider_name: str = "groq", model_name: str = "llama-3.3-70b-versatile") -> LLMClient:
    """Factory helper to retrieve configured LLM client instance."""
    return LLMClient(provider_type=provider_name, model=model_name)


llm_client = LLMClient()
llm = llm_client


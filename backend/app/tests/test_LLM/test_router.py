"""
Jarvis AIOS — LLM Router & Provider Failover Integration Tests
--------------------------------------------------------------

Verifies provider registry, factory instantiation, dynamic chain resolution,
recoverable error failover (Groq -> Ollama), mid-stream safety, and router health checks.
"""

from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from app.LLM.base import (
    ProviderConfig,
    RecoverableLLMError,
)
from app.LLM.factory import provider_factory
from app.LLM.registry import provider_registry
from app.LLM.router import llm_router
from app.LLM.providers.groq_provider import GroqProvider
from app.LLM.providers.ollama_provider import OllamaProvider


def test_provider_registry_and_capabilities():
    assert "groq" in provider_registry.list_providers()
    assert "ollama" in provider_registry.list_providers()

    groq_cls = provider_registry.get("groq")
    assert groq_cls == GroqProvider

    ollama_cls = provider_registry.get("ollama")
    assert ollama_cls == OllamaProvider

    cfg = ProviderConfig(provider_name="groq", model_id="llama-3.3-70b-versatile")
    p_instance = provider_factory.create_provider(cfg)
    caps = p_instance.capabilities
    assert caps.supports_streaming is True
    assert caps.supports_tools is True


def test_llm_router_stateless_resolution():
    chain = llm_router.resolve_provider_chain()
    assert len(chain) >= 2
    assert chain[0].provider_name in ["groq", "ollama"]


def test_router_invoke_recoverable_failover():
    # Mock Groq to raise RecoverableLLMError (429 Rate Limit) and Ollama to succeed
    mock_groq = MagicMock()
    mock_groq.chat.side_effect = RecoverableLLMError("Groq HTTP 429 Rate Limit Exceeded")

    mock_ollama = MagicMock()
    mock_ollama.chat.return_value = AIMessage(content="Response from Ollama Fallback Driver")

    def mock_create_provider(config):
        if config.provider_name == "groq":
            return mock_groq
        return mock_ollama

    with patch("app.LLM.router.ProviderFactory.create_provider", side_effect=mock_create_provider):
        response = llm_router.invoke([HumanMessage(content="Test prompt")])
        assert response.content == "Response from Ollama Fallback Driver"
        assert mock_groq.chat.called
        assert mock_ollama.chat.called


def test_router_stream_pre_token_failover():
    # Mock Groq stream to raise RecoverableLLMError before emitting tokens
    mock_groq = MagicMock()
    mock_groq.stream.side_effect = RecoverableLLMError("Groq Connection Timeout")

    mock_ollama = MagicMock()
    mock_ollama.stream.return_value = iter(["Token1 ", "Token2"])

    def mock_create_provider(config):
        if config.provider_name == "groq":
            return mock_groq
        return mock_ollama

    with patch("app.LLM.router.ProviderFactory.create_provider", side_effect=mock_create_provider):
        tokens = list(llm_router.stream([HumanMessage(content="Test stream")]))
        assert tokens == ["Token1 ", "Token2"]


def test_router_stream_mid_stream_safety():
    # Mock Groq to stream 1 token and then fail mid-stream; should NOT splice Ollama!
    def failing_stream(messages):
        yield "Partial "
        raise RecoverableLLMError("Connection dropped mid-sentence")

    mock_groq = MagicMock()
    mock_groq.stream.side_effect = failing_stream

    mock_ollama = MagicMock()
    mock_ollama.stream.return_value = iter(["Ollama Token"])

    def mock_create_provider(config):
        if config.provider_name == "groq":
            return mock_groq
        return mock_ollama

    with patch("app.LLM.router.ProviderFactory.create_provider", side_effect=mock_create_provider):
        stream_gen = llm_router.stream([HumanMessage(content="Test stream safety")])
        first_token = next(stream_gen)
        assert first_token == "Partial "

        # Second iteration should raise RecoverableLLMError and terminate without splicing Ollama
        try:
            next(stream_gen)
            assert False, "Should have raised exception mid-stream"
        except RecoverableLLMError as exc:
            assert "Connection dropped mid-sentence" in str(exc)
        assert not mock_ollama.stream.called


def test_router_health_check():
    health = llm_router.health_check()
    assert "status" in health
    assert "provider_chain" in health
    assert len(health["provider_chain"]) >= 2

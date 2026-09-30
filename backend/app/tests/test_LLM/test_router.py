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
    assert "nvidia" in provider_registry.list_providers()
    assert "mistral" in provider_registry.list_providers()
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
    assert len(health["provider_chain"]) >= 3


# ==============================================================================
# DETERMINISTIC PROVIDER FAILOVER BOUNDARY TESTS (TESTS 1 - 6)
# ==============================================================================

def _create_mock_providers():
    mock_groq = MagicMock()
    mock_nvidia = MagicMock()
    mock_mistral = MagicMock()
    mock_ollama = MagicMock()

    mock_groq.chat.return_value = AIMessage(content="Groq Response")
    mock_nvidia.chat.return_value = AIMessage(content="NVIDIA NIM Response")
    mock_mistral.chat.return_value = AIMessage(content="Mistral Response")
    mock_ollama.chat.return_value = AIMessage(content="Ollama Response")

    def factory_side_effect(config):
        if config.provider_name == "groq":
            return mock_groq
        elif config.provider_name in ("nvidia", "nvidia-nim", "nim"):
            return mock_nvidia
        elif config.provider_name in ("mistral", "mistralai"):
            return mock_mistral
        elif config.provider_name == "ollama":
            return mock_ollama
        raise ValueError(f"Unknown provider: {config.provider_name}")

    return mock_groq, mock_nvidia, mock_mistral, mock_ollama, factory_side_effect


def test_scenario_1_groq_available():
    """TEST 1: Groq available -> Groq selected."""
    mock_groq, mock_nvidia, mock_mistral, mock_ollama, side_effect = _create_mock_providers()

    with patch("app.LLM.router.ProviderFactory.create_provider", side_effect=side_effect):
        res = llm_router.invoke([HumanMessage(content="Test scenario 1")])
        assert res.content == "Groq Response"
        assert mock_groq.chat.called
        assert not mock_nvidia.chat.called
        assert not mock_mistral.chat.called
        assert not mock_ollama.chat.called


def test_scenario_2_groq_unavailable_nvidia_selected():
    """TEST 2: Groq unavailable -> NVIDIA NIM selected."""
    mock_groq, mock_nvidia, mock_mistral, mock_ollama, side_effect = _create_mock_providers()
    mock_groq.chat.side_effect = RecoverableLLMError("Groq 429 Rate Limit Exceeded")

    with patch("app.LLM.router.ProviderFactory.create_provider", side_effect=side_effect):
        res = llm_router.invoke([HumanMessage(content="Test scenario 2")])
        assert res.content == "NVIDIA NIM Response"
        assert mock_groq.chat.called
        assert mock_nvidia.chat.called
        assert not mock_mistral.chat.called
        assert not mock_ollama.chat.called


def test_scenario_3_groq_and_nvidia_unavailable_mistral_selected():
    """TEST 3: Groq + NVIDIA NIM unavailable -> Mistral selected."""
    mock_groq, mock_nvidia, mock_mistral, mock_ollama, side_effect = _create_mock_providers()
    mock_groq.chat.side_effect = RecoverableLLMError("Groq 503 Service Unavailable")
    mock_nvidia.chat.side_effect = RecoverableLLMError("NVIDIA 429 Quota Exceeded")

    with patch("app.LLM.router.ProviderFactory.create_provider", side_effect=side_effect):
        res = llm_router.invoke([HumanMessage(content="Test scenario 3")])
        assert res.content == "Mistral Response"
        assert mock_groq.chat.called
        assert mock_nvidia.chat.called
        assert mock_mistral.chat.called
        assert not mock_ollama.chat.called


def test_scenario_4_all_remote_unavailable_dev_ollama_selected():
    """TEST 4: Groq + NVIDIA NIM + Mistral unavailable in DEVELOPMENT -> Ollama selected."""
    mock_groq, mock_nvidia, mock_mistral, mock_ollama, side_effect = _create_mock_providers()
    mock_groq.chat.side_effect = RecoverableLLMError("Groq Down")
    mock_nvidia.chat.side_effect = RecoverableLLMError("NVIDIA Down")
    mock_mistral.chat.side_effect = RecoverableLLMError("Mistral Down")

    with patch.dict("os.environ", {"ENVIRONMENT": "development"}):
        with patch("app.LLM.router.ProviderFactory.create_provider", side_effect=side_effect):
            res = llm_router.invoke([HumanMessage(content="Test scenario 4")])
            assert res.content == "Ollama Response"
            assert mock_groq.chat.called
            assert mock_nvidia.chat.called
            assert mock_mistral.chat.called
            assert mock_ollama.chat.called


def test_scenario_5_all_remote_unavailable_prod_ollama_not_selected():
    """TEST 5: Groq + NVIDIA NIM + Mistral unavailable in PRODUCTION -> Ollama MUST NOT be selected."""
    import pytest
    mock_groq, mock_nvidia, mock_mistral, mock_ollama, side_effect = _create_mock_providers()
    mock_groq.chat.side_effect = RecoverableLLMError("Groq Down")
    mock_nvidia.chat.side_effect = RecoverableLLMError("NVIDIA Down")
    mock_mistral.chat.side_effect = RecoverableLLMError("Mistral Down")

    with patch.dict("os.environ", {"ENVIRONMENT": "production"}):
        # Verify Ollama is completely excluded from chain resolution in production
        prod_chain = llm_router.resolve_provider_chain()
        provider_names = [c.provider_name for c in prod_chain]
        assert "ollama" not in provider_names
        assert provider_names == ["groq", "nvidia", "mistral"]

        with patch("app.LLM.router.ProviderFactory.create_provider", side_effect=side_effect):
            with pytest.raises(RecoverableLLMError) as exc_info:
                llm_router.invoke([HumanMessage(content="Test scenario 5")])

            assert "All LLM providers in failover chain exhausted" in str(exc_info.value)
            assert mock_groq.chat.called
            assert mock_nvidia.chat.called
            assert mock_mistral.chat.called
            assert not mock_ollama.chat.called, "Ollama MUST NEVER be called in production!"


def test_scenario_6_no_provider_configured():
    """TEST 6: No provider configured -> existing appropriate configuration/provider error."""
    import pytest
    with patch.object(llm_router, "resolve_provider_chain", return_value=[]):
        with pytest.raises(RecoverableLLMError) as exc_info:
            llm_router.invoke([HumanMessage(content="Test scenario 6")])

        assert "No LLM providers configured" in str(exc_info.value)


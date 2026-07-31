# backend/app/tests/test_Models/test_model_studio.py
"""
Jarvis AIOS — Unit Tests for Model Studio Engine (Sprint 6.6B).
"""

import pytest
from app.Data.base import Base
from app.Data.database import engine, SessionLocal
from app.Models.manager import model_manager
from app.Models.adapters import encrypt_api_key, decrypt_api_key


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup unnecessary in SQLite memory/temp file test setup


def test_credential_encryption():
    raw_key = "sk-proj-1234567890abcdef"
    enc = encrypt_api_key(raw_key)
    assert enc != raw_key
    dec = decrypt_api_key(enc)
    assert dec == raw_key


def test_provider_registration():
    db = SessionLocal()
    try:
        prov = model_manager.register_provider(
            db,
            provider_name="groq_test",
            display_name="Groq Test Provider",
            api_base_url="https://api.groq.com/v1",
            api_key="gsk_test123",
            is_enabled=True,
        )
        assert prov["provider_name"] == "groq_test"
        assert prov["has_api_key"] is True
    finally:
        db.close()


def test_model_registration():
    db = SessionLocal()
    import uuid
    m_id = f"gpt-4o-mini-test-{uuid.uuid4().hex[:6]}"
    try:
        mod = model_manager.create_model_config(
            db,
            provider_name="openai",
            model_id=m_id,
            display_name="GPT-4o Mini Test",
            context_window=128000,
            max_output_tokens=4096,
            input_cost_per_1k=0.00015,
            output_cost_per_1k=0.00060,
            is_default=False,
        )
        assert mod["model_id"] == m_id
        assert mod["provider_name"] == "openai"
    finally:
        db.close()


def test_benchmark_runner():
    db = SessionLocal()
    try:
        res = model_manager.run_benchmark(db, model_id="gemini-2.5-flash", prompt_tokens=150, completion_tokens=300)
        assert res["model_id"] == "gemini-2.5-flash"
        assert res["total_latency_ms"] > 0.0
        assert res["status"] == "success"
    finally:
        db.close()


def test_cost_calculator():
    db = SessionLocal()
    try:
        res = model_manager.calculate_cost(db, model_id="gemini-2.5-flash", prompt_tokens=10000, completion_tokens=2000, monthly_requests=100)
        assert res["prompt_cost"] > 0.0
        assert res["estimated_monthly_cost"] > 0.0
    finally:
        db.close()

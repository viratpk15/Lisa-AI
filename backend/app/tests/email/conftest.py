"""
Jarvis AIOS — Email Intelligence Test Fixtures & Mocks
"""

from typing import Any
import pytest
from langchain_core.messages import AIMessage
from sqlalchemy import select

from app.Data.database import SessionLocal
from app.Data.models import UserModel
from app.Tools.email.guards import reset_rate_limits_for_test
from app.Tools.email.models import (
    EmailAnalysisModel,
    EmailDigestCacheModel,
    EmailModel,
    GmailConnectionModel,
)


class MockLLMClient:
    """Mock LLM client returning controlled text or raising errors."""

    def __init__(self, response_text: str = "") -> None:
        self.response_text = response_text
        self.should_raise: Exception | None = None
        self.invocations: list[list[Any]] = []

    def set_response(self, text: str) -> None:
        self.response_text = text
        self.should_raise = None

    def set_error(self, exc: Exception) -> None:
        self.should_raise = exc

    def invoke(self, messages: Any, **kwargs: Any) -> AIMessage:
        if self.should_raise:
            raise self.should_raise
        return AIMessage(content=self.response_text)


@pytest.fixture(autouse=True)
def clean_email_test_env():
    """Reset rate limits and clean email records for test users 901 and 902."""
    reset_rate_limits_for_test()
    db = SessionLocal()
    try:
        for u_id, email in [(901, "alice.intel@jarvis.test"), (902, "bob.intel@jarvis.test")]:
            existing = db.execute(select(UserModel).where(UserModel.id == u_id)).scalar_one_or_none()
            if not existing:
                db.add(UserModel(id=u_id, email=email, password_hash="hashed_pw", created_at="2026-09-27T00:00:00Z"))

        db.query(EmailDigestCacheModel).filter(EmailDigestCacheModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.query(EmailAnalysisModel).filter(
            EmailAnalysisModel.email_id.in_(
                select(EmailModel.id).where(EmailModel.user_id.in_([901, 902]))
            )
        ).delete(synchronize_session=False)
        db.query(EmailModel).filter(EmailModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.query(GmailConnectionModel).filter(GmailConnectionModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()

    yield

    reset_rate_limits_for_test()
    db = SessionLocal()
    try:
        db.query(EmailDigestCacheModel).filter(EmailDigestCacheModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.query(EmailAnalysisModel).filter(
            EmailAnalysisModel.email_id.in_(
                select(EmailModel.id).where(EmailModel.user_id.in_([901, 902]))
            )
        ).delete(synchronize_session=False)
        db.query(EmailModel).filter(EmailModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.query(GmailConnectionModel).filter(GmailConnectionModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()

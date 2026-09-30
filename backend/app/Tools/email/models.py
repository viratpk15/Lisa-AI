"""
Jarvis AIOS — Email Foundation SQLAlchemy Models
------------------------------------------------
Provides database schemas for:
- GmailConnectionModel: Secure OAuth credential references & connection status.
- EmailModel: Parsed email messages with sender, recipients, body, and attachment metadata.
- EmailSenderVerificationModel: Authentication-Results parsing (SPF, DKIM, DMARC).
"""

from typing import Optional
from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Data.base import Base


class GmailConnectionModel(Base):
    """SQLAlchemy model for user Gmail OAuth connection state."""

    __tablename__ = "gmail_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email_address: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_credentials: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="connected")
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(100), nullable=False)
    last_sync_at: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        Index("idx_gmail_conn_user_status", "user_id", "status"),
        UniqueConstraint("user_id", "email_address", name="uq_user_gmail_email"),
    )


class EmailModel(Base):
    """SQLAlchemy model for parsed email message persistence."""

    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gmail_message_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    gmail_thread_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sender: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    sender_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    recipients: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    subject: Mapped[str] = mapped_column(Text, nullable=False, default="")
    body_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    received_at: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    attachment_metadata: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    gmail_metadata: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(100), nullable=False)

    sender_verification: Mapped[Optional["EmailSenderVerificationModel"]] = relationship(
        "EmailSenderVerificationModel",
        back_populates="email",
        uselist=False,
        cascade="all, delete-orphan",
    )
    analysis: Mapped[Optional["EmailAnalysisModel"]] = relationship(
        "EmailAnalysisModel",
        back_populates="email",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "gmail_message_id", name="uq_user_gmail_message_id"),
        Index("idx_emails_user_received", "user_id", "received_at"),
        Index("idx_emails_user_sender_domain", "user_id", "sender_domain"),
    )


class EmailSenderVerificationModel(Base):
    """SQLAlchemy model for SPF, DKIM, DMARC sender verification results."""

    __tablename__ = "email_sender_verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    spf_status: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    spf_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dkim_status: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    dkim_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dmarc_status: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    dmarc_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_auth_results: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")
    verified_at: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped["EmailModel"] = relationship("EmailModel", back_populates="sender_verification")

    __table_args__ = (
        Index("idx_verification_user_email", "user_id", "email_id"),
    )


class EmailAnalysisModel(Base):
    """SQLAlchemy model for LLM classification, summarization, and action extraction."""

    __tablename__ = "email_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    priority_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    summary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_items_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deadline: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    classified_at: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    summarized_at: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    extracted_at: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped["EmailModel"] = relationship("EmailModel", back_populates="analysis")


class EmailDigestCacheModel(Base):
    """SQLAlchemy model for cached email digests ('today' or 'week')."""

    __tablename__ = "email_digest_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period: Mapped[str] = mapped_column(String(20), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "period", name="uq_user_digest_period"),
    )

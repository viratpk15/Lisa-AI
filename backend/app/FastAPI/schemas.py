"""
Jarvis AIOS
-----------
FastAPI Response Schemas

Standardised Pydantic response models for all API endpoints.
All endpoints should return these models for consistent frontend integration.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """A single error detail item.

    Used inside ErrorResponse to provide structured error information
    that can be rendered by the frontend.

    Attributes:
        code: Machine-readable error code (e.g. "invalid_credentials").
        message: Human-readable error description.
        details: Optional additional context (e.g. validation errors).
    """

    code: str = Field(
        ...,
        description="Machine-readable error code for programmatic handling.",
        examples=["invalid_credentials", "session_forbidden", "validation_error"],
    )
    message: str = Field(
        ...,
        description="Human-readable error description.",
        examples=["Invalid or expired token"],
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Optional additional context (e.g. field-level validation errors).",
        examples=[{"field": "email", "reason": "already registered"}],
    )


class ErrorResponse(BaseModel):
    """Standard error response for all API endpoints.

    Every HTTP error response should conform to this schema
    so the frontend can handle errors uniformly.

    Attributes:
        error: The structured error information.
    """

    error: ErrorDetail = Field(
        ...,
        description="Structured error information with code, message, and optional details.",
    )


class ChatResponse(BaseModel):
    """Response model for the chat endpoint.

    Attributes:
        response: The AI-generated response text.
    """

    response: str = Field(
        ...,
        description="The AI assistant's response to the user's message.",
        examples=["The weather today is sunny with a high of 25°C."],
    )


class ConversationSummary(BaseModel):
    """Summary model for a conversation thread used in list endpoints.

    Mirrors the frontend Conversation interface but without the messages array.
    """
    id: str = Field(..., description="Conversation session identifier")
    title: str = Field(..., description="Conversation title")
    preview: str = Field(..., description="Short preview of the latest message")
    time: str = Field(..., description="Human readable timestamp of last activity")
    pinned: bool = Field(..., description="Pinned status for UI ordering")
    model: str = Field(..., description="LLM model used for the conversation")
    unread: bool = Field(..., description="Whether there are unread messages")
    group: str = Field(..., description="Grouping label for UI (Today, Yesterday, etc.)")


class MessageSchema(BaseModel):
    """Single message item within a conversation session thread history."""
    id: str = Field(..., description="Message identifier")
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message text content")
    timestamp: str = Field(default="", description="Human readable timestamp")


class ConversationDetail(ConversationSummary):
    """Detailed model for a single conversation session thread including message history."""
    messages: list[MessageSchema] = Field(default_factory=list, description="Array of messages in this session")


class PaginatedMessagesResponse(BaseModel):
    """Response model for paginated conversation messages requests."""
    messages: list[MessageSchema] = Field(..., description="Chronological list of messages for current page window")
    next_cursor: int | None = Field(default=None, description="ID cursor for requesting older messages page")
    has_more: bool = Field(..., description="Whether older messages exist in history")


class HealthResponse(BaseModel):
    """Response model for the health check endpoint.

    Attributes:
        status: Service health status.
        version: Running version of the application.
    """

    status: str = Field(
        ...,
        description="Service health status.",
        examples=["ok"],
    )
    version: str = Field(
        ...,
        description="Running version of the application.",
        examples=["1.0.0"],
    )


class AttachmentResponse(BaseModel):
    """Response model for uploaded file attachments.

    Attributes:
        id: Unique attachment identifier.
        name: Original filename.
        type: Detected type category (pdf, image, zip, markdown, code).
        sizeBytes: Optional size in bytes.
        urlPlaceholder: Optional URL or path.
    """
    id: str = Field(..., description="Attachment identifier")
    name: str = Field(..., description="Filename")
    type: str = Field(..., description="File category (pdf, image, zip, markdown, code)")
    sizeBytes: int | None = Field(default=None, description="Size in bytes")
    urlPlaceholder: str | None = Field(default=None, description="Access URL or path")

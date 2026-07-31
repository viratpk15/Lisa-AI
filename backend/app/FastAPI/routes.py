"""
Jarvis AIOS
-----------
FastAPI Routes

HTTP endpoints for the chat functionality.
All chat endpoints require authentication.

Every endpoint returns standardised Pydantic response models.
Error responses follow the ErrorResponse schema for consistent
frontend error handling.

POST /chat  — generous rate limit (30/minute)
"""

import logging
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import StreamingResponse

from app.FastAPI.request_models import ChatRequest
from app.FastAPI.schemas import ChatResponse, ErrorResponse, HealthResponse
from app.Services.chat_service import chat
from app.Auth.dependencies import get_current_user
from app.Auth.models import User
from app.FastAPI.dependencies import verify_session_ownership
from app.FastAPI.rate_limiter import limiter
from app.Config.settings import CHAT_RATE_LIMIT
from app.Jarvis.runtime import jarvis

logger = logging.getLogger(__name__)

router = APIRouter()

# Include conversation routes
from app.FastAPI.routes_conversations import router as conversations_router  # noqa: E402
router.include_router(conversations_router)

# NOTE: tools_router is intentionally NOT included here. It is already mounted
# once, at its own /tools prefix, directly in app/main.py. It previously was
# also nested here under /api/v1/tools, which duplicated every tools endpoint
# in the OpenAPI schema and was never called by the frontend (toolApi.ts calls
# plain /tools/...).


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description=(
        "Returns the current health status and running version "
        "of the Jarvis AIOS backend."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Service is healthy and running.",
            "model": HealthResponse,
        },
    },
)
def health_check() -> HealthResponse:
    """Perform a health check on the service.

    Returns:
        HealthResponse with status "ok" and the current version.
    """
    return HealthResponse(status="ok", version="1.0.0")


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a Chat Message",
    description=(
        "Process a chat message within an authenticated session. "
        "The session_id is bound to the authenticated user. If the session "
        "does not exist, it is created. If it exists but belongs to another "
        "user, a 403 Forbidden is returned."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Chat response generated successfully.",
            "model": ChatResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token.",
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Session does not belong to the authenticated user.",
            "model": ErrorResponse,
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Rate limit exceeded. Too many chat requests.",
            "model": ErrorResponse,
        },
    },
)
@limiter.limit(CHAT_RATE_LIMIT)
def chat_route(
    request: Request,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """Process a chat message within an authenticated session.

    The session_id is bound to the authenticated user. If the session
    does not exist, it is created. If it exists but belongs to another
    user, a 403 Forbidden is returned.

    Args:
        request: The incoming request (required by slowapi).
        chat_request: The chat request containing session_id and message.
        current_user: The authenticated user from JWT token.

    Returns:
        The chat response containing the AI-generated answer.

    Raises:
        HTTPException: 403 if session ownership is violated.
    """
    # Verify session ownership before processing
    verify_session_ownership(session_id=chat_request.session_id, current_user=current_user)

    answer = chat(
        session_id=chat_request.session_id,
        message=chat_request.message,
    )

    return ChatResponse(response=answer)


@router.post(
    "/chat/stream",
    summary="Stream Chat Message via SSE",
    description=(
        "Process a chat message within an authenticated session and stream "
        "incremental token response frames via Server-Sent Events (SSE)."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Server-Sent Events stream.",
            "content": {"text/event-stream": {}},
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token.",
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Session does not belong to the authenticated user.",
            "model": ErrorResponse,
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Rate limit exceeded. Too many chat requests.",
            "model": ErrorResponse,
        },
    },
)
@limiter.limit(CHAT_RATE_LIMIT)
async def chat_stream_route(
    request: Request,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """Stream chat tokens in real-time using Server-Sent Events (SSE).

    Validates JWT authentication and session ownership prior to establishing
    the streaming connection. Yields structured SSE events (thinking, token, done, error).
    Detects client disconnects to prevent orphaned generation tasks.
    """
    verify_session_ownership(session_id=chat_request.session_id, current_user=current_user)

    async def event_generator():
        try:
            for event in jarvis.chat_stream(
                session_id=chat_request.session_id,
                message=chat_request.message,
                attachment_ids=chat_request.attachment_ids,
                active_document_id=chat_request.active_document_id,
                active_filename=chat_request.active_filename,
            ):
                if await request.is_disconnected():
                    logger.info("Client disconnected during stream for session %s", chat_request.session_id)
                    break
                yield event
        except Exception as exc:
            logger.error("Streaming route exception for session %s: %s", chat_request.session_id, str(exc))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

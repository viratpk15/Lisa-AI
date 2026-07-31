"""
Jarvis AIOS
-----------
FastAPI Dependencies

Reusable FastAPI dependencies for endpoint protection and validation.
These dependencies are injected via Depends() into route handlers.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.Auth.dependencies import get_current_user
from app.Auth.models import User
from app.Memory.persistence import get_persistence_backend


def verify_session_ownership(
    session_id: str,
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify that a chat session belongs to the authenticated user.

    Chat sessions are bound to the authenticated user who created them.
    If the session does not yet exist, it is considered owned by the
    requesting user (creation-on-demand). If it exists but is bound to
    a different user, a 403 Forbidden is raised.

    Args:
        session_id: The chat session identifier to verify.
        current_user: The authenticated user from JWT token.

    Returns:
        The authenticated User if ownership is confirmed.

    Raises:
        HTTPException: 403 if the session belongs to a different user.
    """
    persistence = get_persistence_backend()
    owner_id = persistence.get_session_owner(session_id)

    if owner_id is not None and owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "session_forbidden",
                    "message": "Session does not belong to the authenticated user",
                }
            },
        )

    return current_user

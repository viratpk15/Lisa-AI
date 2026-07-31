"""
Jarvis AIOS
-----------
Authentication Dependencies

FastAPI dependencies for JWT authentication.
Provides get_current_user() for protected endpoints.
All exceptions return the standardised ErrorResponse schema.

This module does NOT import any Memory components.
Only Auth, FastAPI, and standard library imports are used.
"""

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.Auth.models import User

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme
security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    """Extract and validate the current user from JWT token.

    This dependency extracts the Bearer token from the Authorization header,
    validates it, and returns the User model.

    Args:
        credentials: The HTTP Bearer credentials from FastAPI.

    Returns:
        The authenticated User model.

    Raises:
        HTTPException: 401 with standardised ErrorResponse if token is
            invalid, expired, or has missing claims.
    """
    # Lazy import inside function to avoid eager module-level side effects
    from app.Auth.security import decode_access_token

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except ValueError as e:
        logger.warning("Token validation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "invalid_token",
                    "message": "Invalid or expired token",
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    email = payload.get("email")

    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "invalid_token_payload",
                    "message": "Invalid token payload",
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return User(id=user_id, email=email)

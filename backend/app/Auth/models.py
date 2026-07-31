"""
Jarvis AIOS
-----------
Authentication Models

Pydantic models for user registration, login, and JWT tokens.
All models follow the coding standards for request/response schemas.

Validation notes:
- email: EmailStr provides format validation (no additional trim needed)
- password: min 8 chars (already present), max 128 chars, auto-trimmed
"""

from pydantic import BaseModel, EmailStr, Field
from pydantic import StringConstraints
from typing import Annotated

# Reusable validated string for passwords
PasswordField = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=8,
        max_length=128,
    ),
]


class UserCreate(BaseModel):
    """Request model for user registration.

    Attributes:
        email: User's email address (validated as proper email format).
        password: Plain-text password (8-128 characters, trimmed).
    """

    email: EmailStr
    password: PasswordField = Field(description="Password (8-128 characters, trimmed)")


class User(BaseModel):
    """User model returned by the authentication system.

    Attributes:
        id: Unique user identifier.
        email: User's email address.
    """

    id: int
    email: str


class Token(BaseModel):
    """JWT token response model.

    Attributes:
        access_token: The signed JWT token.
        token_type: Always "bearer" for this implementation.
    """

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Internal model for JWT payload validation.

    Attributes:
        user_id: The user's database ID.
        email: The user's email address.
        exp: Token expiration timestamp.
    """

    user_id: int
    email: str
    exp: int | None = None

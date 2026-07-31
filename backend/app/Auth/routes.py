"""
Jarvis AIOS
-----------
Authentication Routes

FastAPI endpoints for user registration and login.
Every endpoint returns standardised request/response models.
Error responses follow the ErrorResponse schema for consistent frontend handling.

POST /auth/login  — strict rate limit (5/minute)
POST /auth/register — strict rate limit (3/minute)
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.Auth.models import UserCreate, User, Token
from app.Auth.service import auth_service
from app.FastAPI.schemas import ErrorResponse
from app.FastAPI.rate_limiter import limiter
from app.Config.settings import LOGIN_RATE_LIMIT, REGISTER_RATE_LIMIT

router = APIRouter()


@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a New User",
    description="Create a new user account with an email and password.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "User created successfully.",
            "model": User,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Email already registered or invalid input.",
            "model": ErrorResponse,
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Rate limit exceeded. Too many registration attempts.",
            "model": ErrorResponse,
        },
    },
)
@limiter.limit(REGISTER_RATE_LIMIT)
def register(request: Request, user_create: UserCreate) -> User:
    """Register a new user.

    Args:
        request: The incoming request (required by slowapi).
        user_create: The registration request with email and password.

    Returns:
        The created User model.

    Raises:
        HTTPException: 400 if email is already registered.
    """
    try:
        return auth_service.register(
            email=user_create.email,
            password=user_create.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "email_already_registered",
                    "message": str(e),
                }
            },
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate a User",
    description="Authenticate a user with email and password, returning a JWT token.",
    responses={
        status.HTTP_200_OK: {
            "description": "Authentication successful, token returned.",
            "model": Token,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid credentials.",
            "model": ErrorResponse,
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Rate limit exceeded. Too many login attempts.",
            "model": ErrorResponse,
        },
    },
)
@limiter.limit(LOGIN_RATE_LIMIT)
def login(request: Request, user_create: UserCreate) -> Token:
    """Authenticate a user and return a JWT token.

    Args:
        request: The incoming request (required by slowapi).
        user_create: The login request with email and password.

    Returns:
        A Token containing the access token.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    try:
        return auth_service.login(
            email=user_create.email,
            password=user_create.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "invalid_credentials",
                    "message": str(e),
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

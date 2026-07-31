# Authentication

> Jarvis AIOS — Authentication Subsystem  
> Version 1.0

---

## Overview

The authentication subsystem provides user registration, login, and
JWT-based session management. It is designed as a self-contained package
( `app.Auth` ) with a clear layered architecture:

- **Models** — Pydantic schemas for request/response validation.
- **Security** — Password hashing (bcrypt) and JWT creation/verification.
- **Database** — SQLite-backed user storage with parameterized queries.
- **Service** — Business logic coordinating database and security layers.
- **Dependencies** — FastAPI dependency injection for protected endpoints.
- **Routes** — FastAPI router exposing register and login endpoints.

---

## Architecture

```text
FastAPI Router (app.Auth.routes)
        │
        ▼
AuthService (app.Auth.service)
        │
        ├──► UserDatabase (app.Auth.database) — SQLite storage
        │
        └──► Security (app.Auth.security)
                  ├── hash_password / verify_password — bcrypt
                  └── create_access_token / decode_access_token — HS256 JWT
```

### Layering Rules

1. **Routes** call the service only. They never touch the database or
   security layer directly.
2. **Service** coordinates database and security. It contains all business
   logic.
3. **Database** is a pure data-access layer. It has no business logic.
4. **Security** is stateless utility functions. No side effects.

---

## Models

All models are defined in `app.Auth.models`.

| Model | Purpose | Fields |
|---|---|---|
| `UserCreate` | Registration / login request | `email: EmailStr`, `password: str (min 8)` |
| `User` | User representation | `id: int`, `email: str` |
| `Token` | JWT response | `access_token: str`, `token_type: str = "bearer"` |
| `TokenPayload` | Internal JWT payload | `user_id: int`, `email: str`, `exp: int \| None` |

---

## Endpoints

### `POST /auth/register`

Register a new user.

| Attribute | Value |
|---|---|
| Request body | `UserCreate` |
| Response | `201 Created` — `User` |
| Error | `400 Bad Request` — email already registered |
| Error | `422 Unprocessable Entity` — validation failure |

**Example:**

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure_password_123"}'
```

### `POST /auth/login`

Authenticate and receive a JWT.

| Attribute | Value |
|---|---|
| Request body | `UserCreate` |
| Response | `200 OK` — `Token` |
| Error | `401 Unauthorized` — invalid credentials |

**Example:**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure_password_123"}'
```

---

## JWT Details

- **Algorithm:** HS256
- **Secret:** Configured via `JWT_SECRET_KEY` environment variable
- **Expiration:** Configurable via `JWT_EXPIRE_HOURS` (default: 24 hours)
- **Payload claims:** `user_id`, `email`, `exp`

### Token validation

Protected endpoints use the `get_current_user` FastAPI dependency. It
extracts the Bearer token from the `Authorization` header, decodes and
validates it, and returns the `User` model. Invalid or expired tokens
result in a `401 Unauthorized` response.

---

## Session Ownership

Chat sessions are bound to the authenticated user who creates them. The
`SessionOwnership` schema ( `app.FastAPI.schemas` ) verifies that a
`session_id` belongs to the `user_id` making the request.

- **New session** — No owner recorded. Passes verification (will be
  created and bound on first use).
- **Existing session, matching owner** — Passes.
- **Existing session, different owner** — Fails with `403 Forbidden`.

Session binding is handled by `SQLitePersistenceBackend.bind_session_to_user()`
in the memory persistence layer.

---

## Configuration

All authentication settings are in `app.Config.settings` and loaded from
environment variables (or `.env` file):

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET_KEY` | (required) | HS256 signing key |
| `JWT_ALGORITHM` | `HS256` | Signing algorithm |
| `JWT_EXPIRE_HOURS` | `24` | Token lifetime in hours |
| `AUTH_DB_PATH` | `./data/auth.db` | SQLite database path |

### Generating a secret key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Security Considerations

1. **Passwords** are hashed with bcrypt before storage. Plaintext passwords
   are never persisted.
2. **SQL injection** is prevented through parameterized queries.
3. **JWT secret** must be set in the environment. The application will not
   start signing tokens without it.
4. **Token expiry** prevents replay attacks with stale tokens.
5. **Session isolation** prevents one user from accessing another user's
   chat sessions.

---

## Dependencies

- `bcrypt` — Password hashing
- `PyJWT` — JSON Web Token encoding/decoding
- `pydantic[email]` — Email validation
- `python-dotenv` — Environment variable loading

---

## Testing

Authentication tests are located in `backend/app/tests/test_Auth/`.

```bash
# Run all auth tests
cd backend && python -m pytest app/tests/test_Auth/ -v

# Run a specific test class
cd backend && python -m pytest app/tests/test_Auth/test_auth.py::TestRegistration -v
```

### Test coverage

| Category | Tests |
|---|---|
| Registration | Valid registration, password hashing, empty password rejection, min-length validation |
| Duplicate email | Re-registration blocked, different emails allowed |
| Login success | Token returned, payload correctness, expiry claim present |
| Login failure | Wrong password, nonexistent email, invalid hash |
| JWT validation | Valid decode, expired token, malformed token, wrong secret, empty token |
| Unauthorized access | Invalid token in dependency, expired token in dependency |
| Session ownership | New session allowed, owner matches, owner mismatch |
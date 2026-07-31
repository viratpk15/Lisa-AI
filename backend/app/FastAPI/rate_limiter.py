"""
Jarvis AIOS
-----------
Rate Limiter

In-memory rate limiting using slowapi.
No Redis or distributed infrastructure required for v1.0.

The limiter is configured with key_func=client_ip to throttle per IP.
Middleware is added in main.py and decorators are applied per-route.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Single limiter instance shared across all routes.
# The backend uses an in-memory moving window (slowapi.MemoryStorage).
limiter = Limiter(key_func=get_remote_address)

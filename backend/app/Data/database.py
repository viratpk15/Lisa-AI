"""
Jarvis AIOS
-----------
Database Engine & Session Management

Provides SQLAlchemy engine, session maker, and health connection verification
supporting both SQLite (local development) and PostgreSQL / Supabase (production).
"""

import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.Config.settings import DATABASE_PROVIDER, DATABASE_URL, PERSISTENCE_DB_PATH

logger = logging.getLogger(__name__)


def get_connection_url() -> str:
    """Resolve the active database connection URL based on configuration.

    Returns:
        Formatted database URL for SQLAlchemy engine creation.
    """
    if DATABASE_PROVIDER == "postgres" and DATABASE_URL:
        url = DATABASE_URL
        # Normalize driver scheme for psycopg 3.x
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        return url

    # Default to SQLite local database
    return f"sqlite:///{PERSISTENCE_DB_PATH}"


# Create engine based on provider configuration
connection_url = get_connection_url()
is_sqlite = connection_url.startswith("sqlite")

engine_kwargs = {}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(connection_url, **engine_kwargs)

if is_sqlite:
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency generator for obtaining an isolated database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict[str, str | None]:
    """Verify database connection health.

    Returns:
        Dict containing status, provider, server version, or error message.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

            # Fetch server version
            version_str = "unknown"
            try:
                ver_res = conn.execute(text("SELECT version()"))
                row = ver_res.fetchone()
                if row:
                    version_str = str(row[0])
            except Exception:
                version_str = "SQLite Engine"

            return {
                "status": "connected",
                "provider": DATABASE_PROVIDER,
                "version": version_str,
                "error": None,
            }
    except Exception as exc:
        logger.error("Database connection verification failed: %s", exc)
        return {
            "status": "disconnected",
            "provider": DATABASE_PROVIDER,
            "version": None,
            "error": str(exc),
        }

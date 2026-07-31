import os
import logging
from app.Config.settings import PERSISTENCE_DB_PATH
from app.Memory.persistence.base import IPersistenceBackend

logger = logging.getLogger(__name__)


def get_persistence_backend() -> IPersistenceBackend:
    """Lazily construct and return the active persistence backend provider.

    Returns:
        Instance of IPersistenceBackend (SQLitePersistenceBackend or PostgreSQLPersistenceBackend).

    Raises:
        ValueError: If DATABASE_PROVIDER is invalid or unsupported.
    """
    provider = os.getenv("DATABASE_PROVIDER", "sqlite").lower()

    if provider == "postgres":
        logger.info("Lazily initializing PostgreSQL persistence provider")
        from app.Memory.persistence.postgres_backend import PostgreSQLPersistenceBackend

        return PostgreSQLPersistenceBackend()

    if provider == "sqlite":
        logger.info("Lazily initializing SQLite persistence provider (path=%s)", PERSISTENCE_DB_PATH)
        from app.Memory.persistence.sqlite_backend import SQLitePersistenceBackend

        return SQLitePersistenceBackend(db_path=PERSISTENCE_DB_PATH)

    raise ValueError(
        f"Unsupported DATABASE_PROVIDER: '{provider}'. "
        f"Supported providers are 'sqlite' and 'postgres'."
    )

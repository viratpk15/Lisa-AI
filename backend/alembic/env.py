from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Lazily import app metadata — only needed for `alembic revision --autogenerate`.
# Hand-written migrations (upgrade/downgrade) work fine with target_metadata=None.
# This also prevents macOS sandbox/provenance errors on upgrade.
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # backend/
    from app.Data.base import Base as SABase         # noqa: E402
    from app.Data import models as _data_models      # noqa: F401, E402  — registers existing tables
    from app.Agents import models as _agent_models   # noqa: F401, E402  — registers Agent Studio tables
    from app.Memory import models as _memory_models  # noqa: F401, E402  — registers Memory Studio tables
    from app.Models import models as _model_models  # noqa: F401, E402  — registers Model Studio tables
    from app.Workflows import models as _wf_models   # noqa: F401, E402  — registers Workflow Studio tables
    from app.Deployments import models as _dep_models # noqa: F401, E402  — registers Deployment Studio tables
    from app.Data.database import get_connection_url  # noqa: E402
    target_metadata = SABase.metadata                # single registry; all models share this Base
    config.set_main_option("sqlalchemy.url", get_connection_url())
except Exception:
    # Autogenerate won't work, but upgrade/downgrade will succeed.
    target_metadata = None



# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=False,
            compare_nullable=False,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

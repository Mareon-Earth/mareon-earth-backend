from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from app.core.config import get_settings
from app.infrastructure.database import Base


# --------------------------------
# Alembic Config
# --------------------------------

config = context.config

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url_sync)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogeneration
target_metadata = Base.metadata

# --------------------------------
# Migration Runners
# --------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# --------------------------------
# Entrypoint
# --------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

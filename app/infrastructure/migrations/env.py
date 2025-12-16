from logging.config import fileConfig

from google.cloud.sql.connector import Connector, IPTypes
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

    connect_args = {}
    config_section = config.get_section(config.config_ini_section, {})

    if settings.db_mode == "cloudsql_iam":
        # Create a sync connector for migration context
        ip_type = (
            IPTypes.PRIVATE
            if settings.db_connector_ip_type == "PRIVATE"
            else IPTypes.PUBLIC
        )
        connector = Connector(ip_type=ip_type)

        def get_conn():
            return connector.connect(
                settings.cloud_sql_instance,
                "pg8000",
                user=settings.db_iam_user,
                db=settings.db_name,
                enable_iam_auth=True,
            )

        # Inject the creator into the engine configuration
        connect_args["creator"] = get_conn

    connectable = engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        **connect_args,
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

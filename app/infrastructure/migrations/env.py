from logging.config import fileConfig

from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context

from app.core.config import get_settings
from app.infrastructure.database import Base

config = context.config
settings = get_settings()

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = (
        "postgresql+pg8000://"
        if settings.db_mode == "cloudsql_iam"
        else settings.database_url_sync
    )

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
    if settings.db_mode == "cloudsql_iam":
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
                user=settings.migration_iam_user,
                db=settings.db_name,
                enable_iam_auth=True,
            )

        connectable = create_engine(
            "postgresql+pg8000://",
            creator=get_conn,
            poolclass=pool.NullPool,
        )
    else:
        # IMPORTANT: make sure this URL includes a driver, e.g. postgresql+pg8000://
        connectable = create_engine(
            settings.database_url_sync,
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

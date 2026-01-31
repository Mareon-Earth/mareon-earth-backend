from logging.config import fileConfig

from alembic import context

from app.core.config import get_settings
from app.infrastructure.db.session_manager import Base
from app.infrastructure.db.engine_factory import EngineFactory

from app.domain.users.models import User
from app.domain.organization.models import Organization, OrganizationMember
from app.domain.document.models import Document, DocumentFile
from app.domain.vessel.models import Vessel, VesselIdentity

config = context.config
settings = get_settings()

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This generates SQL scripts without connecting to the database.
    """
    factory = EngineFactory(settings)
    url = factory.get_offline_url()

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
    """
    Run migrations in 'online' mode.
    
    Creates an actual database connection and runs migrations.
    """
    factory = EngineFactory(settings)
    connectable = factory.create_sync_engine()

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

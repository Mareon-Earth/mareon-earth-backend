from collections.abc import AsyncGenerator
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    pass


if settings.db_mode == "cloudsql_iam":
    # Initialize connector instance
    _ip_type = (
        IPTypes.PRIVATE
        if settings.db_connector_ip_type == "PRIVATE"
        else IPTypes.PUBLIC
    )
    _connector = Connector(ip_type=_ip_type)

    async def get_cloud_sql_connection():
        return await _connector.connect_async(
            settings.cloud_sql_instance,
            "asyncpg",
            user=settings.db_iam_user,
            db=settings.db_name,
            enable_iam_auth=True,
        )

    engine = create_async_engine(
        "postgresql+asyncpg://",
        async_creator=get_cloud_sql_connection,
        echo=False,
        pool_pre_ping=True,
    )
else:
    engine = create_async_engine(
        settings.database_url_async,
        echo=False,
        pool_pre_ping=True,
    )


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

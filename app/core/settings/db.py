from typing import Literal
from pydantic_settings import BaseSettings

from app.core.exceptions.base import ConfigurationError


class DatabaseSettings(BaseSettings):
    db_mode: Literal["local_url", "cloudsql_iam"] = "local_url"

    # Driver for sync connections (migrations)
    # e.g. "postgresql+psycopg" (default) or "postgresql+pg8000"
    db_driver_sync: str = "postgresql+psycopg"

    # Mode A: Local URL
    database_url: str = ""

    # Mode B: Cloud SQL
    cloud_sql_instance: str = ""
    db_name: str = ""
    db_iam_user: str = ""
    db_connector_ip_type: Literal["PUBLIC", "PRIVATE"] = "PRIVATE"

    # DB Pool
    db_pool_size: int = 5
    db_max_overflow: int = 5
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_pool_pre_ping: bool = True

    @property
    def database_url_sync(self) -> str:
        """
        Returns the sync database URL (useful for Alembic).
        """
        if self.db_mode == "local_url":
            return self.database_url

        if self.db_mode == "cloudsql_iam":
            # For Cloud SQL IAM, Alembic often needs the specific driver in the URL
            # while the Connector handles the socket.
            return f"{self.db_driver_sync}://"

        return ""

    @property
    def database_url_async(self) -> str:
        """
        Returns the async database URL.
        Auto-converts psycopg/standard schemes to asyncpg if running locally.
        """
        if self.db_mode == "local_url" and self.database_url:
            # If user manually set a sync driver in DATABASE_URL, replace it
            url = self.database_url
            if "postgresql+psycopg://" in url:
                return url.replace("postgresql+psycopg://", "postgresql+asyncpg://")
            if "postgresql+pg8000://" in url:
                return url.replace("postgresql+pg8000://", "postgresql+asyncpg://")
            if "postgresql://" in url:
                return url.replace("postgresql://", "postgresql+asyncpg://")
            return url

        if self.db_mode == "cloudsql_iam":
            # Cloud SQL connector handles the connection, return dialect base
            return "postgresql+asyncpg://"

        return self.database_url

    def validate_db(self):
        missing = []
        if self.db_mode == "local_url" and not self.database_url:
            missing.append("DATABASE_URL")

        if self.db_mode == "cloudsql_iam":
            if not self.cloud_sql_instance:
                missing.append("CLOUD_SQL_INSTANCE")
            if not self.db_name:
                missing.append("DB_NAME")
            if not self.db_iam_user:
                missing.append("DB_IAM_USER")

        if missing:
            raise ConfigurationError(
                f"Missing required DB env vars: {', '.join(missing)}"
            )

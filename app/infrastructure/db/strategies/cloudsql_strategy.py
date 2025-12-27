"""
Google Cloud SQL connection strategy with IAM authentication.

Provides connection management for Google Cloud SQL instances using
the Cloud SQL Python Connector with IAM-based authentication.
"""

from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.exceptions.base import ConfigurationError
from app.core.settings.db import DatabaseSettings


class CloudSQLConnectionStrategy:
    """
    Connection strategy for Google Cloud SQL with IAM authentication.
    
    This strategy is designed for:
    - Production deployments on Google Cloud Platform
    - Cloud SQL instances with IAM authentication
    - Automatic connection management via Cloud SQL Connector
    
    Features:
    - IAM-based authentication (no password management)
    - Automatic SSL/TLS encryption
    - Connection pooling and management
    - Support for both private and public IP connections
    - Separate IAM users for application and migrations
    """

    def __init__(self, settings: DatabaseSettings):
        """
        Initialize Cloud SQL connection strategy.
        
        Args:
            settings: Database configuration settings including Cloud SQL details
        """
        self.settings = settings
        self._connector: Connector | None = None

    def validate(self) -> None:
        """
        Validate Cloud SQL connection requirements.
        
        Raises:
            ConfigurationError: If any required Cloud SQL settings are missing
        """
        missing = []
        if not self.settings.cloud_sql_instance:
            missing.append("CLOUD_SQL_INSTANCE")
        if not self.settings.db_name:
            missing.append("DB_NAME")
        if not self.settings.db_iam_user:
            missing.append("DB_IAM_USER")
        if not self.settings.migration_iam_user:
            missing.append("MIGRATION_IAM_USER")

        if missing:
            raise ConfigurationError(
                f"Missing required Cloud SQL settings: {', '.join(missing)}"
            )

    def _get_ip_type(self) -> IPTypes:
        """
        Convert string IP type configuration to IPTypes enum.
        
        Returns:
            IPTypes.PRIVATE for private IP connections,
            IPTypes.PUBLIC for public IP connections
        """
        return (
            IPTypes.PRIVATE
            if self.settings.db_connector_ip_type == "PRIVATE"
            else IPTypes.PUBLIC
        )

    def _get_connector(self) -> Connector:
        """
        Lazy initialization of Cloud SQL Connector singleton.

        The connector manages the connection pool and handles IAM authentication,
        SSL/TLS encryption, and connection lifecycle.
        
        Returns:
            Initialized Connector instance
        """
        if self._connector is None:
            self._connector = Connector(ip_type=self._get_ip_type())
        return self._connector

    async def _create_async_connection(self):
        """
        Connection factory for async connections using asyncpg.

        This is called by SQLAlchemy to create new connections.
        Uses the application IAM user for regular operations.
        
        Returns:
            Async database connection with IAM authentication
        """
        connector = self._get_connector()
        return await connector.connect_async(
            self.settings.cloud_sql_instance,
            "asyncpg",
            user=self.settings.db_iam_user,
            db=self.settings.db_name,
            enable_iam_auth=True,
        )

    def _create_sync_connection(self):
        """
        Connection factory for sync connections using pg8000.

        This is used for migrations and other synchronous operations.
        Uses the migration IAM user which may have elevated privileges.
        
        Returns:
            Sync database connection with IAM authentication
        """
        connector = self._get_connector()
        return connector.connect(
            self.settings.cloud_sql_instance,
            "pg8000",
            user=self.settings.migration_iam_user,
            db=self.settings.db_name,
            enable_iam_auth=True,
        )

    def create_async_engine(self) -> AsyncEngine:
        """
        Create async engine using Cloud SQL Connector.

        The connector handles authentication and connection management,
        so we provide a minimal URL and use async_creator to delegate
        connection creation to the connector.
        
        Returns:
            AsyncEngine with Cloud SQL Connector integration
        """
        return create_async_engine(
            "postgresql+asyncpg://",
            async_creator=self._create_async_connection,
            echo=False,
            pool_pre_ping=self.settings.db_pool_pre_ping,
            pool_size=self.settings.db_pool_size,
            max_overflow=self.settings.db_max_overflow,
            pool_timeout=self.settings.db_pool_timeout,
            pool_recycle=self.settings.db_pool_recycle,
        )

    def create_sync_engine(self) -> Engine:
        """
        Create sync engine using Cloud SQL Connector for migrations.

        Uses NullPool since migrations don't benefit from connection pooling
        and we want each migration to have a fresh connection.
        
        Returns:
            Engine with Cloud SQL Connector integration and no pooling
        """
        return create_engine(
            "postgresql+pg8000://",
            creator=self._create_sync_connection,
            poolclass=pool.NullPool,
        )

    def get_offline_url(self) -> str:
        """
        Get URL for offline migrations.

        For Cloud SQL, offline migrations don't actually connect,
        so we just return the dialect specification for Alembic to use
        when generating SQL scripts.
        
        Returns:
            Minimal PostgreSQL URL for offline operations
        """
        return "postgresql+pg8000://"

    async def close(self) -> None:
        """
        Close the Cloud SQL Connector and release resources.

        This should be called during application shutdown to ensure
        all connections are properly closed and resources are released.

        Best Practice: Integrate with FastAPI's lifespan context manager.
        """
        if self._connector is not None:
            await self._connector.close_async()
            self._connector = None

    async def __aenter__(self):
        """Support async context manager protocol."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensure connector is closed when exiting context."""
        await self.close()
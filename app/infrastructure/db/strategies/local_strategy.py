"""
Local database connection strategy.

Provides connection management for standard PostgreSQL connection strings,
automatically handling driver selection (asyncpg for async, pg8000 for sync).
"""

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.exceptions.base import ConfigurationError
from app.core.settings.db import DatabaseSettings


class LocalConnectionStrategy:
    """
    Connection strategy for local database using standard connection string.
    
    This strategy is ideal for:
    - Local development environments
    - Direct PostgreSQL connections
    - Standard database URL connections
    
    The strategy automatically normalizes URLs to use the appropriate driver:
    - asyncpg for async operations (high performance)
    - pg8000 for sync operations (migrations, pure Python)
    """

    def __init__(self, settings: DatabaseSettings):
        """
        Initialize local connection strategy.
        
        Args:
            settings: Database configuration settings
        """
        self.settings = settings

    def validate(self) -> None:
        """
        Validate local connection requirements.
        
        Raises:
            ConfigurationError: If DATABASE_URL is not set
        """
        if not self.settings.database_url:
            raise ConfigurationError(
                "DATABASE_URL is required when db_mode='local_url'"
            )

    def _normalize_url_for_driver(self, url: str, driver: str) -> str:
        """
        Convert URL to use specified driver.

        Takes a connection URL and ensures it uses the specified driver.
        Handles common PostgreSQL URL formats:
        - postgresql://... -> postgresql+{driver}://...
        - postgresql+asyncpg://... -> postgresql+{driver}://...
        
        Args:
            url: Original database URL
            driver: Target driver (e.g., 'asyncpg', 'pg8000')
            
        Returns:
            URL string with normalized driver specification
        """
        if not url or "://" not in url:
            return url

        # Split protocol and connection parts
        parts = url.split("://", 1)
        protocol = parts[0].split("+")[0]  # Get base protocol (e.g., 'postgresql')
        connection_part = parts[1]

        return f"{protocol}+{driver}://{connection_part}"

    def create_async_engine(self) -> AsyncEngine:
        """
        Create async engine with asyncpg driver for high-performance async operations.
        
        Uses connection pooling optimized for async operations with configurable
        pool size, timeout, and recycling settings.
        
        Returns:
            AsyncEngine configured with asyncpg driver and pool settings
        """
        url = self._normalize_url_for_driver(self.settings.database_url, "asyncpg")

        return create_async_engine(
            url,
            echo=False,
            pool_pre_ping=self.settings.db_pool_pre_ping,
            pool_size=self.settings.db_pool_size,
            max_overflow=self.settings.db_max_overflow,
            pool_timeout=self.settings.db_pool_timeout,
            pool_recycle=self.settings.db_pool_recycle,
        )

    def create_sync_engine(self) -> Engine:
        """
        Create sync engine with pg8000 driver for migrations (pure Python driver).
        
        Uses NullPool since migrations don't benefit from connection pooling
        and should have fresh connections for each operation.
        
        Returns:
            Engine configured with pg8000 driver and no pooling
        """
        url = self._normalize_url_for_driver(self.settings.database_url, "pg8000")

        return create_engine(
            url,
            poolclass=pool.NullPool,  # Migrations don't need connection pooling
        )

    def get_offline_url(self) -> str:
        """
        Get URL for offline migrations (no actual connection needed).
        
        Returns:
            URL string with pg8000 driver for offline migration script generation
        """
        return self._normalize_url_for_driver(self.settings.database_url, "pg8000")
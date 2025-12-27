"""
Database engine factory for creating SQLAlchemy engines.

This module provides a central factory that selects and uses the appropriate
connection strategy based on configuration, ensuring validation happens
before any engine creation.
"""

from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.exceptions.base import ConfigurationError
from app.core.settings.db import DatabaseSettings
from app.infrastructure.db.protocols import ConnectionStrategy
from app.infrastructure.db.strategies import (
    CloudSQLConnectionStrategy,
    LocalConnectionStrategy,
)


class EngineFactory:
    """
    Factory for creating database engines based on configuration.

    This factory:
    1. Selects the appropriate connection strategy based on db_mode
    2. Validates configuration before creating any engines
    3. Provides a single point of access for engine creation
    4. Encapsulates all connection logic behind a clean interface
    """

    def __init__(self, settings: DatabaseSettings):
        """
        Initialize factory with settings and select appropriate strategy.

        Args:
            settings: Database configuration settings

        Raises:
            ConfigurationError: If db_mode is unknown or configuration is invalid
        """
        self.settings = settings
        self.strategy: ConnectionStrategy = self._get_strategy()

    def _get_strategy(self) -> ConnectionStrategy:
        """
        Select and validate appropriate connection strategy.

        Returns:
            Configured and validated connection strategy

        Raises:
            ConfigurationError: If db_mode is unknown or validation fails
        """
        if self.settings.db_mode == "local_url":
            strategy = LocalConnectionStrategy(self.settings)
        elif self.settings.db_mode == "cloudsql_iam":
            strategy = CloudSQLConnectionStrategy(self.settings)
        else:
            raise ConfigurationError(
                f"Unknown db_mode: {self.settings.db_mode}. "
                f"Valid options: 'local_url', 'cloudsql_iam'"
            )

        # Validate configuration before returning strategy
        strategy.validate()
        return strategy

    def create_async_engine(self) -> AsyncEngine:
        """
        Create async SQLAlchemy engine using selected strategy.

        This engine is used for the main application's async operations.

        Returns:
            Configured async SQLAlchemy engine
        """
        return self.strategy.create_async_engine()

    def create_sync_engine(self) -> Engine:
        """
        Create sync SQLAlchemy engine using selected strategy.

        This engine is used for migrations and other synchronous operations.

        Returns:
            Configured sync SQLAlchemy engine
        """
        return self.strategy.create_sync_engine()

    def get_offline_url(self) -> str:
        """
        Get database URL for offline migrations.

        Offline migrations generate SQL scripts without connecting to the database.

        Returns:
            Database URL string appropriate for offline migrations
        """
        return self.strategy.get_offline_url()
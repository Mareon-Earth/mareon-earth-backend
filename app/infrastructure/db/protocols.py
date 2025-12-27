"""
Database connection strategy protocol.

Defines the interface that all connection strategies must implement,
following the Strategy Pattern and Protocol-Based Design.
"""

from typing import Protocol, runtime_checkable

from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine


@runtime_checkable
class ConnectionStrategy(Protocol):
    """
    Protocol defining database connection strategy interface.
    
    This protocol ensures all connection strategies provide consistent
    methods for engine creation and validation, regardless of the
    underlying connection mechanism (local URL, Cloud SQL, etc.).
    """

    def create_async_engine(self) -> AsyncEngine:
        """
        Create and configure async SQLAlchemy engine for application use.
        
        Returns:
            AsyncEngine configured with appropriate pool settings
        """
        ...

    def create_sync_engine(self) -> Engine:
        """
        Create and configure sync SQLAlchemy engine for migrations.
        
        Returns:
            Engine configured for synchronous operations (typically migrations)
        """
        ...

    def validate(self) -> None:
        """
        Validate required configuration for this strategy.
        
        Raises:
            ConfigurationError: If required settings are missing or invalid
        """
        ...

    def get_offline_url(self) -> str:
        """
        Get URL string for offline migrations.
        
        Returns:
            Database URL string suitable for Alembic offline mode
        """
        ...
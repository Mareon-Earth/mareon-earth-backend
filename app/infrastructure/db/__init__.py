"""
Database infrastructure module.

Provides clean exports for all database-related functionality:
- Base ORM model class
- Session management utilities
- Engine factory for advanced use cases
- Connection strategies and protocols
- Lifespan management for proper cleanup
"""

from app.infrastructure.db.engine_factory import EngineFactory
from app.infrastructure.db.protocols import ConnectionStrategy
from app.infrastructure.db.session_manager import (
    AsyncSessionLocal,
    Base,
    engine,
    get_db_session,
    database_lifespan,
)
from app.infrastructure.db.strategies import (
    CloudSQLConnectionStrategy,
    LocalConnectionStrategy,
)

__all__ = [
    # ORM Base
    "Base",
    # Session Management
    "get_db_session",
    "AsyncSessionLocal",
    "engine",
    "database_lifespan",
    # Factory & Protocols
    "EngineFactory",
    "ConnectionStrategy",
    # Strategies
    "LocalConnectionStrategy",
    "CloudSQLConnectionStrategy",
]
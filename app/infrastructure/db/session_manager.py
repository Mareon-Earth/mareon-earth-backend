"""
Database session management.

Provides the SQLAlchemy engine, session factory, and dependency injection
utilities for database access throughout the application.

This module follows the Session-per-Request pattern for FastAPI applications.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager # Added import

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings
from app.infrastructure.db.engine_factory import EngineFactory


settings = get_settings()

# Type alias for session factory
SessionManager = async_sessionmaker[AsyncSession]


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    
    All domain models should inherit from this class to gain
    SQLAlchemy's declarative mapping capabilities.
    """
    pass


# Create engine using factory - all connection logic is encapsulated
factory = EngineFactory(settings)
engine = factory.create_async_engine()

# Session factory for dependency injection
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get a database session.
    
    This function is designed to be used with FastAPI's dependency injection:
    
    Usage:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db_session)):
            result = await db.execute(select(User))
            return result.scalars().all()
    
    The session is automatically closed when the request completes,
    ensuring proper connection management.
    
    Yields:
        AsyncSession: Database session for the current request
    """
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def database_lifespan():
    """
    Lifespan context manager for database connections.

    Ensures proper cleanup of database resources (connections, pools, etc.)
    when the application shuts down.

    Usage in FastAPI:
        from app.infrastructure.db import database_lifespan

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            async with database_lifespan():
                yield

        app = FastAPI(lifespan=lifespan)

    This is especially important for Cloud SQL Connector which needs
    to be explicitly closed to release resources.
    """
    # Startup: Resources are already initialized
    yield

    # Shutdown: Clean up resources
    await engine.dispose()

    # If using Cloud SQL, close the connector
    from app.infrastructure.db.strategies import CloudSQLConnectionStrategy
    if isinstance(factory.strategy, CloudSQLConnectionStrategy):
        await factory.strategy.close()
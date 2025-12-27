"""
Database connection strategy implementations.

This module provides concrete implementations of the ConnectionStrategy protocol:
- LocalConnectionStrategy: Standard connection string-based connections
- CloudSQLConnectionStrategy: Google Cloud SQL with IAM authentication
"""

from app.infrastructure.db.strategies.cloudsql_strategy import CloudSQLConnectionStrategy
from app.infrastructure.db.strategies.local_strategy import LocalConnectionStrategy

__all__ = [
    "LocalConnectionStrategy",
    "CloudSQLConnectionStrategy",
]
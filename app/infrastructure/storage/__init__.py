# infrastructure/storage/__init__.py
from .client import StorageClient
from .protocols import StorageProtocol
from .gcs import GCSStorage
from .exceptions import (
    StorageError,
    StorageFileNotFoundError,
    SignedUrlError,
    StorageDeleteError,
    StorageAuthenticationError,
)
from functools import lru_cache
from app.core.config import StorageSettings

__all__ = [
    "StorageClient",
    "StorageProtocol",
    "GCSStorage",
    "get_storage_client",
    "StorageError",
    "StorageFileNotFoundError",
    "SignedUrlError",
    "StorageDeleteError",
    "StorageAuthenticationError",
]

@lru_cache
def get_storage_client() -> StorageClient:
    """Get cached storage client instance."""
    return StorageClient.from_config(StorageSettings())
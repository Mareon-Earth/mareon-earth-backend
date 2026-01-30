# app/dependencies/storage.py
from app.infrastructure.storage import get_storage_client, StorageClient

__all__ = ["get_storage_client", "StorageClient"]
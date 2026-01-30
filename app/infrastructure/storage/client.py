from .protocols import StorageProtocol
from .gcs import GCSStorage
from app.core.config import StorageSettings


class StorageClient:
    """Factory and wrapper for storage operations."""
    
    def __init__(self, storage: StorageProtocol):
        """
        Initialize storage client.
        
        Args:
            storage: Storage implementation (GCS, S3, etc.)
        """
        self._storage = storage
    
    @classmethod
    def from_config(cls, config: StorageSettings) -> "StorageClient":
        """Create storage client from configuration."""
        storage = GCSStorage(
            bucket_name=config.gcs_bucket_name
        )
        return cls(storage)
    
    async def generate_signed_url(self, path: str, **kwargs) -> str:
        """Generate a signed URL for reading a file."""
        return await self._storage.generate_signed_url(path, **kwargs)
    
    async def generate_upload_url(self, path: str, content_type: str, content_md5: str, **kwargs) -> str:
        """Generate a signed URL for uploading a file."""
        return await self._storage.generate_upload_url(path, content_type, content_md5, **kwargs)
    
    async def delete_file(self, path: str) -> bool:
        """Delete a file from storage."""
        return await self._storage.delete_file(path)
    
    async def file_exists(self, path: str) -> bool:
        """Check if a file exists in storage."""
        return await self._storage.file_exists(path)
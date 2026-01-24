from functools import lru_cache
from typing import Optional, Dict, Any
from clerk_backend_api import Clerk
from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_clerk() -> Clerk:
    """
    Get cached Clerk client instance.
    Uses bearer authentication with Clerk secret key.
    """
    settings = get_settings()
    return Clerk(bearer_auth=settings.clerk_secret_key)


async def update_user_metadata(
    user_id: str, 
    public_metadata: Optional[Dict[str, Any]] = None, 
    private_metadata: Optional[Dict[str, Any]] = None
) -> Optional[Any]:
    """
    Update Clerk user metadata (public and/or private).
    """
    clerk = get_clerk()
    
    # Build the params dict with only non-None values
    params: Dict[str, Any] = {}
    if public_metadata is not None:
        params["public_metadata"] = public_metadata
    if private_metadata is not None:
        params["private_metadata"] = private_metadata
    
    if not params:
        return None
    
    # Use the native async method from Clerk SDK
    return await clerk.users.update_metadata_async(
        user_id=user_id,
        **params
    )


async def update_organization_metadata(
    organization_id: str,
    public_metadata: Optional[Dict[str, Any]] = None,
    private_metadata: Optional[Dict[str, Any]] = None
) -> Optional[Any]:
    """
    Update Clerk organization metadata (public and/or private).
    """
    clerk = get_clerk()
    
    # Build the params dict with only non-None values
    params: Dict[str, Any] = {}
    if public_metadata is not None:
        params["public_metadata"] = public_metadata
    if private_metadata is not None:
        params["private_metadata"] = private_metadata
    
    if not params:
        return None
    
    # Use the native async method from Clerk SDK (merge_metadata_async)
    return await clerk.organizations.merge_metadata_async(
        organization_id=organization_id,
        **params
    )
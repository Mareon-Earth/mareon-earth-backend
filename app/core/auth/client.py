from functools import lru_cache
from clerk_backend_api import Clerk
from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_clerk() -> Clerk:
    settings = get_settings()
    return Clerk(bearer_auth=settings.clerk_secret_key)

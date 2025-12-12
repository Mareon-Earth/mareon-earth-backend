from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # General
    env: str = "dev"

    # Database
    database_url_sync: str = ""     # For Alembic (psycopg)
    database_url_async: str = ""    # For runtime (asyncpg)

    # Clerk
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    clerk_webhook_secret: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def ensure_valid(self) -> "Settings":
        """
        Runtime sanity check so we still treat these as 'required'
        even though we gave defaults for the type checker.
        """
        missing = []

        if not self.database_url_sync:
            missing.append("DATABASE_URL_SYNC")

        if not self.database_url_async:
            missing.append("DATABASE_URL_ASYNC")

        if not self.clerk_secret_key:
            missing.append("CLERK_SECRET_KEY")

        if not self.clerk_publishable_key:
            missing.append("CLERK_PUBLISHABLE_KEY")

        if not self.clerk_webhook_secret:  # <-- NEW
            missing.append("CLERK_WEBHOOK_SECRET")

        if missing:
            missing_str = ", ".join(missing)
            raise RuntimeError(f"Missing required env vars: {missing_str}")

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached settings object. Called without args,
    but we don't get static type errors because fields have defaults.
    """
    return Settings().ensure_valid()

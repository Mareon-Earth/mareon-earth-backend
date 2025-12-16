from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.settings.app import AppSettings
from app.core.settings.auth import AuthSettings
from app.core.settings.db import DatabaseSettings
from app.core.settings.log import LogSettings


class Settings(AppSettings, AuthSettings, DatabaseSettings, LogSettings, BaseSettings):
    """
    Main Settings class that combines all modular settings.
    This keeps the codebase clean while maintaining a single entry point for config.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def ensure_valid(self) -> "Settings":
        """
        Runtime sanity check for required variables.
        Delegates validation to individual modules.
        """
        self.validate_db()
        self.validate_auth()
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings().ensure_valid()

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
        Runtime validation for required configuration.
        
        Database validation happens via EngineFactory instantiation,
        which validates mode-specific requirements before creating engines.
        """
        # Validate auth settings
        self.validate_auth()
        
        # Database validation happens when EngineFactory is instantiated
        # This is done in database.py and migrations/env.py
        # The factory will raise ConfigurationError if settings are invalid
        
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance with validation."""
    return Settings().ensure_valid()

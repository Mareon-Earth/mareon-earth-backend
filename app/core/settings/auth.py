from pydantic_settings import BaseSettings

from app.core.exceptions.base import ConfigurationError


class AuthSettings(BaseSettings):
    auth_enabled: bool = True
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    clerk_webhook_secret: str = ""

    def validate_auth(self):
        if self.auth_enabled:
            missing = []
            if not self.clerk_secret_key:
                missing.append("CLERK_SECRET_KEY")
            if not self.clerk_publishable_key:
                missing.append("CLERK_PUBLISHABLE_KEY")
            if not self.clerk_webhook_secret:
                missing.append("CLERK_WEBHOOK_SECRET")

            if missing:
                raise ConfigurationError(
                    f"Missing required auth env vars: {', '.join(missing)}"
                )

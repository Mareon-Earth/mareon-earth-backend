from typing import Literal
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_name: str = "mareon-api"
    app_env: Literal["local", "prod"] = "local"
    port: int = 8000
    api_v1_prefix: str = "/api/v1"

    @property
    def is_local(self) -> bool:
        return self.app_env == "local"

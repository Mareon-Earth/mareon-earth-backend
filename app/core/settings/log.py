from pydantic_settings import BaseSettings


class LogSettings(BaseSettings):
    log_level: str = "INFO"
    json_logs: bool = False

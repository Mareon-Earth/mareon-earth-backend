from fastapi import status


# core/exceptions/base.py
class MareonError(Exception):
    message = "An error occurred."
    code = "UNKNOWN_ERROR"
    status_code = 400  # int is enough

    def __init__(self, message: str | None = None, metadata: dict | None = None):
        if message:
            self.message = message
        self.metadata = metadata


class ConfigurationError(MareonError):
    """
    Raised when application configuration is invalid at startup.
    """

    message = "Configuration error."
    code = "CONFIG_ERROR"
    status_code = 500

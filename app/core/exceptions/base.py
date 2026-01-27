class MareonError(Exception):
    message = "An error occurred."
    code = "UNKNOWN_ERROR"
    status_code = 400

    def __init__(self, message: str | None = None, metadata: dict | None = None):
        self.message = message or self.message
        self.metadata = metadata
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "metadata": self.metadata,
        }


class ConfigurationError(MareonError):
    message = "Configuration error."
    code = "CONFIG_ERROR"
    status_code = 500

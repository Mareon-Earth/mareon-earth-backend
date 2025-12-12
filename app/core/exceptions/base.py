from fastapi import status


class MareonError(Exception):
    """
    Base error for all domain/service exceptions.
    Not domain-specific.
    """

    message = "An error occurred."
    code = "UNKNOWN_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str | None = None, metadata: dict | None = None):
        if message:
            self.message = message
        self.metadata = metadata

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "metadata": self.metadata,
        }

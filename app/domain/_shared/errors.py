class DomainError(Exception):
    code = "DOMAIN_ERROR"
    message = "A domain error occurred."

    def __init__(self, message: str | None = None, metadata: dict | None = None):
        self.message = message or self.message
        self.metadata = metadata
        super().__init__(self.message)

class NotFound(DomainError):
    code = "NOT_FOUND"
    message = "Resource not found."

class Conflict(DomainError):
    code = "CONFLICT"
    message = "Conflict."

class Forbidden(DomainError):
    code = "FORBIDDEN"
    message = "Forbidden."
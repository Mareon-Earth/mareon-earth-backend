class DomainError(Exception):
    code = "DOMAIN_ERROR"
    message = "A domain error occurred."
    def __init__(self, message: str | None = None, metadata: dict | None = None):
        if message:
            self.message = message
        self.metadata = metadata

class NotFound(DomainError):
    code = "NOT_FOUND"
    message = "Resource not found."

class Conflict(DomainError):
    code = "CONFLICT"
    message = "Conflict."

class Forbidden(DomainError):
    code = "FORBIDDEN"
    message = "Forbidden."
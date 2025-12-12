from .base import MareonError

class NotFoundError(MareonError):
    message = "Resource not found."
    status_code = 404
    code = "NOT_FOUND"

class UnauthorizedError(MareonError):
    message = "Unauthorized."
    status_code = 401
    code = "UNAUTHORIZED"

class ForbiddenError(MareonError):
    message = "Forbidden."
    status_code = 403
    code = "FORBIDDEN"

class ConflictError(MareonError):
    message = "Conflict."
    status_code = 409
    code = "CONFLICT"

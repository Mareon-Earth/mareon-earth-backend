from app.core.exceptions.http import UnauthorizedError, ForbiddenError


class MissingAuthTokenError(UnauthorizedError):
    message = "Missing session token (Authorization Bearer token or __session cookie)."
    code = "AUTH_MISSING_TOKEN"


class InvalidAuthTokenError(UnauthorizedError):
    message = "Invalid or expired session token."
    code = "AUTH_INVALID_TOKEN"


class MissingOrganizationError(ForbiddenError):
    message = "This endpoint requires an active organization."
    code = "AUTH_MISSING_ORG"


class PendingOrganizationError(ForbiddenError):
    message = "User is not yet in an organization (sts=pending)."
    code = "AUTH_ORG_PENDING"

class WebhookSignatureError(UnauthorizedError):
    message = "Invalid webhook signature."
    code = "AUTH_WEBHOOK_INVALID_SIGNATURE"

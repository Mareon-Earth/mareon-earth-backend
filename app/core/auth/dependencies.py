from fastapi import Depends, Request

from app.core.auth.context import AuthContext
from app.core.auth.exceptions import MissingOrganizationError, PendingOrganizationError, InvalidAuthTokenError
from app.core.auth.tokens import verify_request_with_clerk


async def get_auth_context(request: Request) -> AuthContext:
    payload = await verify_request_with_clerk(request)

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidAuthTokenError(metadata={"missing": "sub"})

    # org-scoped always
    org_id = payload.get("org_id")
    if not org_id:
        raise MissingOrganizationError()

    if payload.get("sts") == "pending":
        raise PendingOrganizationError()

    return AuthContext(
        user_id=user_id,
        organization_id=org_id,
        organization_role=payload.get("org_role"),
        session_id=payload.get("sid"),
    )


# Optional version (nice for mixed public/private endpoints)
async def get_optional_auth_context(request: Request) -> AuthContext | None:
    try:
        return await get_auth_context(request)
    except Exception:
        return None

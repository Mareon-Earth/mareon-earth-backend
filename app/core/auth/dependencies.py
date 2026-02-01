from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.context import AuthContext
from app.core.auth.exceptions import (
    MissingOrganizationError,
    PendingOrganizationError,
    InvalidAuthTokenError,
)
from app.core.auth.tokens import verify_request_with_clerk
from app.infrastructure.db import get_db_session
from app.domain.users.repository import UserRepository
from app.domain.organization.repository import OrganizationRepository


async def get_auth_context(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> AuthContext:
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

    # Resolve Internal User ID
    internal_user_id = payload.get("public_metadata", {}).get("user_id")
    user_source = "session"

    if not internal_user_id:
        # Fallback to DB
        user_repo = UserRepository(db)
        user = await user_repo.get_by_clerk_id(user_id)
        if user:
            internal_user_id = user.id
            user_source = "db"

    print(f"[Auth] Resolved User ID {internal_user_id} from {user_source}")

    # Resolve Internal Org ID
    internal_org_id = payload.get("org_public_metadata", {}).get("org_id")
    org_source = "session"

    if not internal_org_id and org_id:
        # Fallback to DB
        org_repo = OrganizationRepository(db)
        org = await org_repo.get_by_clerk_id(org_id)
        if org:
            internal_org_id = org.id
            org_source = "db"

    print(f"[Auth] Resolved Org ID {internal_org_id} from {org_source}")

    return AuthContext(
        user_id=user_id,
        organization_id=org_id,
        organization_role=payload.get("org_role"),
        session_id=payload.get("sid"),
        internal_user_id=internal_user_id,
        internal_org_id=internal_org_id,
    )


# Optional version (nice for mixed public/private endpoints)
async def get_optional_auth_context(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> AuthContext | None:
    try:
        return await get_auth_context(request, db)
    except Exception:
        return None
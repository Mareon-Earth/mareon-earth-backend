from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.client import update_user_metadata, update_organization_metadata
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
    # Check custom claim 'user_public_metadata' first (user config), then fallback
    user_metadata = payload.get("user_public_metadata") or {}
    if not isinstance(user_metadata, dict):
        user_metadata = {}
    
    internal_user_id = user_metadata.get("user_id") or payload.get("public_metadata", {}).get("user_id")
    user_source = "session"

    if not internal_user_id:
        # Fallback to DB
        user_repo = UserRepository(db)
        user = await user_repo.get_by_clerk_id(user_id)
        if user:
            internal_user_id = user.id
            user_source = "db"
            # Self-healing: Sync to Clerk metadata so next token has it
            try:
                print(f"[Auth] Self-healing: Syncing internal user_id to Clerk for {user_id}")
                await update_user_metadata(user_id, public_metadata={"user_id": user.id})
            except Exception as e:
                print(f"[Auth] Failed to sync user metadata: {e}")

    print(f"[Auth] Resolved User ID {internal_user_id} from {user_source}")

    # Resolve Internal Org ID
    # Check custom claim 'org_public_metadata' first (user config), then fallback
    org_metadata = payload.get("org_public_metadata") or {}
    if not isinstance(org_metadata, dict):
        org_metadata = {}

    internal_org_id = org_metadata.get("org_id") or payload.get("organization", {}).get("public_metadata", {}).get("org_id")
    org_source = "session"

    if not internal_org_id and org_id:
        # Fallback to DB
        org_repo = OrganizationRepository(db)
        org = await org_repo.get_by_clerk_id(org_id)
        if org:
            internal_org_id = org.id
            org_source = "db"
            # Self-healing: Sync to Clerk metadata so next token has it
            try:
                print(f"[Auth] Self-healing: Syncing internal org_id to Clerk for {org_id}")
                await update_organization_metadata(org_id, public_metadata={"org_id": org.id})
            except Exception as e:
                print(f"[Auth] Failed to sync org metadata: {e}")

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
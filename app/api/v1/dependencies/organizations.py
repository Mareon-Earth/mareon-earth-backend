from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext, get_auth_context
from app.infrastructure.db import get_db_session
from app.domain.organization.service.protocols import OrganizationServiceProtocol
from app.domain.organization.dependencies import build_organization_service


def get_organization_service(
    db: AsyncSession = Depends(get_db_session),
) -> OrganizationServiceProtocol:
    return build_organization_service(db=db)


def get_authed_organization_service(
    db: AsyncSession = Depends(get_db_session),
    ctx: AuthContext = Depends(get_auth_context),
) -> OrganizationServiceProtocol:
    return build_organization_service(db=db, ctx=ctx)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext
from app.domain.organization.service.organization_service import OrganizationService
from app.domain.organization.service.protocols import OrganizationServiceProtocol
from app.domain.organization.repository import (
    OrganizationRepository,
    OrganizationMemberRepository,
)


def build_organization_service(
    db: AsyncSession,
    ctx: AuthContext | None = None,
) -> OrganizationServiceProtocol:
    org_repo = OrganizationRepository(db)
    member_repo = OrganizationMemberRepository(db)
    return OrganizationService(
        db=db,
        organizations=org_repo,
        org_members=member_repo,
        ctx=ctx,
    )
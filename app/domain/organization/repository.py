from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.domain.organization.models import Organization, OrganizationMember
from app.domain.organization.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
)
from app.domain.protocols.repositories import (
    OrganizationRepositoryProtocol,
    OrganizationMemberRepositoryProtocol,
)


class OrganizationRepository(OrganizationRepositoryProtocol):
    async def get_by_clerk_id(self, db: AsyncSession, clerk_id: str) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.clerk_id == clerk_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, org_id: str) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.id == org_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, data: OrganizationCreate) -> Organization:
        org = Organization(
            clerk_id=data.clerk_id,
            name=data.name,
            description=data.description,
            logo_url=data.logo_url,
        )
        db.add(org)
        await db.flush()
        return org

    async def update(self, db: AsyncSession, org: Organization, data: OrganizationUpdate) -> Organization:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(org, field, value)
        await db.flush()
        return org

    async def delete(self, db: AsyncSession, org: Organization) -> None:
        await db.delete(org)
        await db.flush()


class OrganizationMemberRepository(OrganizationMemberRepositoryProtocol):
    async def get_by_user_and_org(
        self, db: AsyncSession, user_id: str, org_id: str
    ) -> Optional[OrganizationMember]:
        stmt = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.org_id == org_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, data: OrganizationMemberCreate) -> OrganizationMember:
        member = OrganizationMember(
            user_id=data.user_id,
            org_id=data.org_id,
            role=data.role,
        )
        db.add(member)
        await db.flush()
        return member

    async def update(
        self, db: AsyncSession, member: OrganizationMember, data: OrganizationMemberUpdate
    ) -> OrganizationMember:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(member, field, value)
        await db.flush()
        return member

    async def delete(self, db: AsyncSession, member: OrganizationMember) -> None:
        await db.delete(member)
        await db.flush()
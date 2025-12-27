from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.organization.models import Organization, OrgMember
from app.domain.organization.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrgMemberCreate,
    OrgMemberUpdate,
)


class OrganizationRepository:
    """Database layer for the Organization domain."""

    @staticmethod
    async def get_by_clerk_id(db: AsyncSession, clerk_id: str) -> Organization | None:
        stmt = select(Organization).where(Organization.clerk_id == clerk_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, org_id: str) -> Organization | None:
        stmt = select(Organization).where(Organization.id == org_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id_with_members(
        db: AsyncSession, org_id: str
    ) -> Organization | None:
        stmt = (
            select(Organization)
            .where(Organization.id == org_id)
            .options(selectinload(Organization.members))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: OrganizationCreate) -> Organization:
        org = Organization(
            clerk_id=data.clerk_id,
            name=data.name,
            description=data.description,
            logo_url=data.logo_url,
        )
        db.add(org)
        await db.commit()
        await db.refresh(org)
        return org

    @staticmethod
    async def update(
        db: AsyncSession, org: Organization, data: OrganizationUpdate
    ) -> Organization:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(org, field, value)

        await db.commit()
        await db.refresh(org)
        return org

    @staticmethod
    async def delete(db: AsyncSession, org: Organization) -> None:
        await db.delete(org)
        await db.commit()

    @staticmethod
    async def list_user_organizations(
        db: AsyncSession, user_id: str
    ) -> list[Organization]:
        stmt = (
            select(Organization)
            .join(OrgMember)
            .where(OrgMember.user_id == user_id)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


class OrgMemberRepository:
    """Database layer for the OrgMember domain."""

    @staticmethod
    async def get(
        db: AsyncSession, user_id: str, org_id: str
    ) -> OrgMember | None:
        stmt = select(OrgMember).where(
            and_(OrgMember.user_id == user_id, OrgMember.org_id == org_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: OrgMemberCreate) -> OrgMember:
        member = OrgMember(
            user_id=data.user_id,
            org_id=data.org_id,
            role=data.role,
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def update(
        db: AsyncSession, member: OrgMember, data: OrgMemberUpdate
    ) -> OrgMember:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(member, field, value)

        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def delete(db: AsyncSession, member: OrgMember) -> None:
        await db.delete(member)
        await db.commit()

    @staticmethod
    async def list_org_members(db: AsyncSession, org_id: str) -> list[OrgMember]:
        stmt = select(OrgMember).where(OrgMember.org_id == org_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def list_user_memberships(db: AsyncSession, user_id: str) -> list[OrgMember]:
        stmt = select(OrgMember).where(OrgMember.user_id == user_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.domain.organization.models import Organization, OrganizationRole
from app.domain.organization.schemas import OrganizationCreate, OrganizationUpdate
from app.domain.organization.repository import (
    OrganizationRepository,
    OrganizationMemberRepository,
)
from app.domain.organization.exceptions import OrganizationNotFoundError, OrganizationMemberNotFoundError
from app.domain.organization.schemas import OrganizationMemberCreate, OrganizationMemberUpdate


class OrganizationService:
    def __init__(self):
        self.org_repo = OrganizationRepository()
        self.member_repo = OrganizationMemberRepository()

    async def get_or_create_from_clerk(
        self, db: AsyncSession, payload: OrganizationCreate
    ) -> Organization:
        existing = await self.org_repo.get_by_clerk_id(db, payload.clerk_id)
        if existing:
            return existing

        org = await self.org_repo.create(db, payload)
        await db.commit()
        await db.refresh(org)
        return org

    async def get_organization(self, db: AsyncSession, clerk_id: str) -> Organization:
        org = await self.org_repo.get_by_clerk_id(db, clerk_id)
        if not org:
            raise OrganizationNotFoundError()
        return org
    
    async def update_organization(
        self, db: AsyncSession, clerk_id: str, payload: OrganizationUpdate
    ) -> Organization:
        org = await self.org_repo.get_by_clerk_id(db, clerk_id)
        if not org:
            raise OrganizationNotFoundError()

        updated = await self.org_repo.update(db, org, payload)
        await db.commit()
        await db.refresh(updated)
        return updated

    async def delete_organization(self, db: AsyncSession, clerk_id: str) -> None:
        org = await self.org_repo.get_by_clerk_id(db, clerk_id)
        if not org:
            raise OrganizationNotFoundError()

        await self.org_repo.delete(db, org)
        await db.commit()

    async def add_member(
        self, db: AsyncSession, user_id: str, org_id: str, role: OrganizationRole
    ) -> None:
        """Add a user to an organization with specified role, or update role if already a member."""
        # Check if membership already exists
        existing = await self.member_repo.get_by_user_and_org(db, user_id, org_id)
        if existing:
            # Update role if it changed
            if existing.role != role:
                await self.member_repo.update(
                    db, existing, OrganizationMemberUpdate(role=role)
                )
                await db.commit()
            return

        # Create new membership
        payload = OrganizationMemberCreate(user_id=user_id, org_id=org_id, role=role)
        await self.member_repo.create(db, payload)
        await db.commit()

    async def update_member_role(
        self, db: AsyncSession, user_id: str, org_id: str, role: OrganizationRole
    ) -> None:
        """Update a member's role in an organization."""
        member = await self.member_repo.get_by_user_and_org(db, user_id, org_id)
        if not member:
            raise OrganizationMemberNotFoundError()

        await self.member_repo.update(db, member, OrganizationMemberUpdate(role=role))
        await db.commit()

    async def remove_member(self, db: AsyncSession, user_id: str, org_id: str) -> None:
        """Remove a user from an organization."""
        member = await self.member_repo.get_by_user_and_org(db, user_id, org_id)
        if not member:
            raise OrganizationMemberNotFoundError()

        await self.member_repo.delete(db, member)
        await db.commit()
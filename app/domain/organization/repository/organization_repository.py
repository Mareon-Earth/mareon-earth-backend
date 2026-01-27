from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.organization.models import Organization
from app.domain.organization.repository.protocols import OrganizationRepositoryProtocol


class OrganizationRepository(OrganizationRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: Organization) -> Organization:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: str) -> Organization | None:
        return await self._db.get(Organization, id)

    async def delete(self, id: str) -> None:
        user = await self.get_by_id(id)
        if user is not None:
            await self._db.delete(user)
            await self._db.flush()

    async def update(self, org: Organization) -> Organization:
        await self._db.flush()
        return org

    async def get_by_clerk_id(self, clerk_org_id: str) -> Organization | None:
        stmt = select(Organization).where(Organization.clerk_id == clerk_org_id)
        res = await self._db.execute(stmt)
        return res.scalar_one_or_none()

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.organization.models import OrganizationMember
from app.domain.organization.repository.protocols import OrganizationMemberRepositoryProtocol


class OrganizationMemberRepository(OrganizationMemberRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: OrganizationMember) -> OrganizationMember:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: str) -> OrganizationMember | None:
        return await self._db.get(OrganizationMember, id)

    async def delete(self, id: str) -> None:
        user = await self.get_by_id(id)
        if user is not None:
            await self._db.delete(user)
            await self._db.flush()

    async def update(self, member: OrganizationMember) -> OrganizationMember:
        await self._db.flush()
        return member
    
    async def get_by_user_and_org(self, user_id: str, org_id: str) -> OrganizationMember | None:
        stmt = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.org_id == org_id
        )
        res = await self._db.execute(stmt)
        return res.scalar_one_or_none()
from __future__ import annotations

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain._shared.types import OrganizationMemberId
from app.domain.organization.models import OrganizationMember
from app.domain.organization.repository.protocols import OrganizationMemberRepositoryProtocol

class OrganizationMemberRepository(OrganizationMemberRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: OrganizationMember) -> OrganizationMember:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: OrganizationMemberId) -> OrganizationMember | None:
        user_id, org_id = id
        stmt = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.org_id == org_id
        )
        res = await self._db.execute(stmt)
        return res.scalar_one_or_none()

    async def delete(self, id: OrganizationMemberId) -> None:
        user_id, org_id = id
        stmt = sa_delete(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.org_id == org_id
        )
        await self._db.execute(stmt)
        await self._db.flush()

    async def update(self, member: OrganizationMember) -> OrganizationMember:
        await self._db.flush()
        return member
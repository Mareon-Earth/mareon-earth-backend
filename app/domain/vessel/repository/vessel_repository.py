from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain._shared.types import VesselId, OrganizationId
from app.domain.vessel.models import Vessel
from app.domain.vessel.repository.protocols import VesselRepositoryProtocol


class VesselRepository(VesselRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: Vessel) -> Vessel:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: VesselId) -> Vessel | None:
        return await self._db.get(Vessel, id)

    async def delete(self, id: VesselId) -> None:
        vessel = await self.get_by_id(id)
        if vessel is not None:
            await self._db.delete(vessel)
            await self._db.flush()

    async def update(self, vessel: Vessel) -> Vessel:
        # ORM tracks changes; flush pushes UPDATEs
        await self._db.flush()
        return vessel

    async def list_by_org(
        self, org_id: OrganizationId, offset: int = 0, limit: int = 20
    ) -> tuple[list[Vessel], int]:
        # Count query
        count_stmt = select(func.count()).select_from(Vessel).where(Vessel.org_id == org_id)
        total = (await self._db.execute(count_stmt)).scalar() or 0

        # Data query
        stmt = (
            select(Vessel)
            .where(Vessel.org_id == org_id)
            .offset(offset)
            .limit(limit)
            .order_by(Vessel.created_at.desc())
        )
        result = await self._db.execute(stmt)
        vessels = list(result.scalars().all())
        return vessels, total

    async def count_by_org(self, org_id: OrganizationId) -> int:
        stmt = select(func.count()).select_from(Vessel).where(Vessel.org_id == org_id)
        return (await self._db.execute(stmt)).scalar() or 0

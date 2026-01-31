from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain._shared.types import VesselId
from app.domain.vessel.models import VesselIdentity
from app.domain.vessel.repository.protocols import VesselIdentityRepositoryProtocol


class VesselIdentityRepository(VesselIdentityRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: VesselIdentity) -> VesselIdentity:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: VesselId) -> VesselIdentity | None:
        return await self._db.get(VesselIdentity, id)

    async def delete(self, id: VesselId) -> None:
        identity = await self.get_by_id(id)
        if identity is not None:
            await self._db.delete(identity)
            await self._db.flush()

    async def update(self, identity: VesselIdentity) -> VesselIdentity:
        await self._db.flush()
        return identity

    async def get_by_imo_number(self, imo_number: str) -> VesselIdentity | None:
        stmt = select(VesselIdentity).where(VesselIdentity.imo_number == imo_number)
        res = await self._db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_mmsi_number(self, mmsi_number: str) -> VesselIdentity | None:
        stmt = select(VesselIdentity).where(VesselIdentity.mmsi_number == mmsi_number)
        res = await self._db.execute(stmt)
        return res.scalar_one_or_none()

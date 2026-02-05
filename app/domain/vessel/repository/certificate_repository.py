from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain._shared.types import VesselId, CertificateId
from app.domain.vessel.models import VesselCertificate
from app.domain.vessel.repository.protocols import VesselCertificateRepositoryProtocol


class VesselCertificateRepository(VesselCertificateRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: VesselCertificate) -> VesselCertificate:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: CertificateId) -> VesselCertificate | None:
        return await self._db.get(VesselCertificate, id)

    async def delete(self, id: CertificateId) -> None:
        cert = await self.get_by_id(id)
        if cert is not None:
            await self._db.delete(cert)
            await self._db.flush()

    async def update(self, certificate: VesselCertificate) -> VesselCertificate:
        await self._db.flush()
        return certificate

    async def list_by_vessel(
        self, vessel_id: VesselId, offset: int = 0, limit: int = 20
    ) -> tuple[list[VesselCertificate], int]:
        count_stmt = (
            select(func.count())
            .select_from(VesselCertificate)
            .where(VesselCertificate.vessel_id == vessel_id)
        )
        total = (await self._db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(VesselCertificate)
            .where(VesselCertificate.vessel_id == vessel_id)
            .offset(offset)
            .limit(limit)
            .order_by(VesselCertificate.expiry_date.asc().nullslast())
        )
        result = await self._db.execute(stmt)
        certificates = list(result.scalars().all())
        return certificates, total
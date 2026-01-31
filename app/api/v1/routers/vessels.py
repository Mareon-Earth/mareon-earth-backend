from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_vessel_service
from app.domain.vessel.schemas import VesselCreate, VesselRead
from app.domain.vessel.service.protocols import VesselServiceProtocol

router = APIRouter(prefix="/vessels", tags=["vessels"])


@router.post("", response_model=VesselRead)
async def create_vessel(
    request: VesselCreate,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.create_vessel(payload=request)
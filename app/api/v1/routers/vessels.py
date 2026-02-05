from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import get_vessel_service
from app.domain._shared import PaginatedResponse
from app.domain.vessel.schemas import (
    VesselCreate,
    VesselRead,
    VesselUpdate,
    VesselListParams,
    VesselIdentityCreate,
    VesselIdentityRead,
    VesselIdentityUpdate,
    VesselDimensionsCreate,
    VesselDimensionsRead,
    VesselDimensionsUpdate,
    VesselCertificateBase,
    VesselCertificateRead,
    VesselCertificateUpdate,
)
from app.domain.vessel.service.protocols import VesselServiceProtocol

router = APIRouter(prefix="/vessels", tags=["vessels"])


# ───────────────────────────────────────────────────────────────────
# Core CRUD
# ───────────────────────────────────────────────────────────────────

@router.post("", response_model=VesselRead)
async def create_vessel(
    request: VesselCreate,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.create_vessel(payload=request)


@router.get("", response_model=PaginatedResponse[VesselRead])
async def list_vessels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: str | None = None,
    vessel_type: str | None = None,
    flag_state: str | None = None,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    params = VesselListParams(
        page=page, page_size=page_size, name=name, vessel_type=vessel_type, flag_state=flag_state
    )
    return await svc.list_vessels(params=params)


@router.get("/{vessel_id}", response_model=VesselRead)
async def get_vessel(
    vessel_id: str,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.get_vessel(vessel_id=vessel_id)


@router.patch("/{vessel_id}", response_model=VesselRead)
async def update_vessel(
    vessel_id: str,
    request: VesselUpdate,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.update_vessel(vessel_id=vessel_id, payload=request)


@router.delete("/{vessel_id}", status_code=204)
async def delete_vessel(
    vessel_id: str,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    await svc.delete_vessel(vessel_id=vessel_id)


# ───────────────────────────────────────────────────────────────────
# Identity management
# ───────────────────────────────────────────────────────────────────

@router.put("/{vessel_id}/identity", response_model=VesselIdentityRead)
async def upsert_identity(
    vessel_id: str,
    request: VesselIdentityCreate,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.upsert_identity(vessel_id=vessel_id, payload=request)


@router.patch("/{vessel_id}/identity", response_model=VesselIdentityRead)
async def update_identity(
    vessel_id: str,
    request: VesselIdentityUpdate,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.update_identity(vessel_id=vessel_id, payload=request)


@router.delete("/{vessel_id}/identity", status_code=204)
async def delete_identity(
    vessel_id: str,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    await svc.delete_identity(vessel_id=vessel_id)


# ───────────────────────────────────────────────────────────────────
# Dimensions management
# ───────────────────────────────────────────────────────────────────

@router.put("/{vessel_id}/dimensions", response_model=VesselDimensionsRead)
async def upsert_dimensions(
    vessel_id: str,
    request: VesselDimensionsCreate,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.upsert_dimensions(vessel_id=vessel_id, payload=request)


@router.patch("/{vessel_id}/dimensions", response_model=VesselDimensionsRead)
async def update_dimensions(
    vessel_id: str,
    request: VesselDimensionsUpdate,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.update_dimensions(vessel_id=vessel_id, payload=request)


@router.delete("/{vessel_id}/dimensions", status_code=204)
async def delete_dimensions(
    vessel_id: str,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    await svc.delete_dimensions(vessel_id=vessel_id)

# ───────────────────────────────────────────────────────────────────
# Certificate management
# ───────────────────────────────────────────────────────────────────

@router.get("/{vessel_id}/certificates", response_model=PaginatedResponse[VesselCertificateRead])
async def list_certificates(
    vessel_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.list_certificates(vessel_id=vessel_id, page=page, page_size=page_size)

@router.post("/{vessel_id}/certificates", response_model=VesselCertificateRead, status_code=201)
async def create_certificate(
    vessel_id: str,
    request: VesselCertificateBase,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.create_certificate(vessel_id=vessel_id, payload=request)

@router.get("/{vessel_id}/certificates/{certificate_id}", response_model=VesselCertificateRead)
async def get_certificate(
    vessel_id: str,
    certificate_id: str,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.get_certificate(vessel_id=vessel_id, certificate_id=certificate_id)

@router.patch("/{vessel_id}/certificates/{certificate_id}", response_model=VesselCertificateRead)
async def update_certificate(
    vessel_id: str,
    certificate_id: str,
    request: VesselCertificateUpdate,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    return await svc.update_certificate(
        vessel_id=vessel_id, certificate_id=certificate_id, payload=request
    )

@router.delete("/{vessel_id}/certificates/{certificate_id}", status_code=204)
async def delete_certificate(
    vessel_id: str,
    certificate_id: str,
    svc: VesselServiceProtocol = Depends(get_vessel_service),
):
    await svc.delete_certificate(vessel_id=vessel_id, certificate_id=certificate_id)
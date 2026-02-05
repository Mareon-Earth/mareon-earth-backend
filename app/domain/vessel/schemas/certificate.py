from __future__ import annotations

from app.domain._shared.types import Date, DateTime
from pydantic import Field

from app.domain._shared import RequestSchema, ResponseSchema
from app.domain.vessel.enums import CertificateDomain, CertificateStatus

class VesselCertificateBase(RequestSchema):
    """Vessel certificate entry extracted from class status reports."""

    domain: CertificateDomain = Field(..., description="Certificate group (e.g., CLASS, STATUTORY).")
    description: str = Field(..., description="Certificate name as stated in the document.")
    identifier: str | None = Field(None, description="Certificate identifier (e.g., DNV code or ABS number).")
    issuer: str | None = Field(None, description="Issuing authority (e.g., DNV, ABS, Flag State).")
    issued_date: Date | None = Field(None, description="Issue date, if stated.")
    expiry_date: Date | None = Field(None, description="Expiry or valid-until date, if stated.")
    status: CertificateStatus = Field(CertificateStatus.UNKNOWN, description="Certificate status.")

class VesselCertificateCreate(VesselCertificateBase):
    """Create a certificate for a specific vessel."""

    vessel_id: str = Field(..., description="ID of the vessel this certificate belongs to.")

class VesselCertificateUpdate(RequestSchema):
    """Partial update for vessel certificate."""
    domain: CertificateDomain | None = None
    description: str | None = None
    identifier: str | None = None
    issuer: str | None = None
    issued_date: Date | None = None
    expiry_date: Date | None = None
    status: CertificateStatus | None = None


class VesselCertificateRead(ResponseSchema):
    id: str
    vessel_id: str

    domain: CertificateDomain
    description: str
    identifier: str | None
    issuer: str | None
    issued_date: Date | None
    expiry_date: Date | None
    status: CertificateStatus

    created_at: DateTime
    updated_at: DateTime

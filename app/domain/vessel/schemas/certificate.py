from __future__ import annotations

from datetime import date, datetime
from pydantic import Field

from app.domain._shared import RequestSchema, ResponseSchema
from app.domain.vessel.enums import CertificateDomain, CertificateStatus

class VesselCertificateBase(RequestSchema):
    """
    Vessel certificate entry extracted from class status reports.
    Keep fields generic to cover DNV/ABS/BV formats.
    """

    domain: CertificateDomain = Field(
        ...,
        description="Certificate group (e.g., CLASS, STATUTORY). Infer from section header if needed.",
    )
    description: str = Field(
        ...,
        description="Certificate name as stated in the document.",
    )
    identifier: str | None = Field(
        None,
        description="Certificate identifier (e.g., DNV code or ABS certificate number).",
    )
    issuer: str | None = Field(
        None,
        description="Issuing authority (e.g., DNV, ABS, Flag State). Infer from document source if not explicit.",
    )
    issued_date: date | None = Field(
        None,
        description="Issue date, if stated.",
    )
    expiry_date: date | None = Field(
        None,
        description="Expiry or valid-until date, if stated.",
    )
    status: CertificateStatus = Field(
        CertificateStatus.UNKNOWN,
        description="Certificate status. Map report wording to enum; use UNKNOWN if unclear.",
    )

class VesselCertificateCreate(VesselCertificateBase):
    """Create a certificate for a specific vessel."""

    vessel_id: str = Field(
        ...,
        description="ID of the vessel this certificate belongs to.",
    )


class VesselCertificateRead(ResponseSchema):
    id: str
    vessel_id: str

    domain: CertificateDomain
    description: str
    identifier: str | None
    issuer: str | None
    issued_date: date | None
    expiry_date: date | None
    status: CertificateStatus

    created_at: datetime
    updated_at: datetime

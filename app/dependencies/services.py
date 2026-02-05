# app/dependencies/services.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext, get_auth_context
from app.infrastructure.db import get_db_session
from app.infrastructure.storage import StorageClient, get_storage_client

# ── Repositories (internal only — not exposed to routers) ─────────────────────
from app.domain.users.repository import UserRepository
from app.domain.organization.repository import (
    OrganizationRepository,
    OrganizationMemberRepository,
)
from app.domain.document.repository import (
    DocumentRepository,
    DocumentFileRepository,
)

from app.domain.vessel.repository import (
    VesselRepository,
    VesselIdentityRepository,
    VesselDimensionsRepository,
    VesselCertificateRepository,
)

# ── Services & Protocols ──────────────────────────────────────────────────────
from app.domain.users.service.user_service import UserService
from app.domain.users.service.protocols import UserServiceProtocol

from app.domain.organization.service.organization_service import OrganizationService
from app.domain.organization.service.protocols import OrganizationServiceProtocol

from app.domain.document.service.document_service import DocumentService
from app.domain.document.service.protocols import DocumentServiceProtocol

from app.domain.vessel.service.vessel_service import VesselService
from app.domain.vessel.service.protocols import VesselServiceProtocol


# ── Private factory functions ─────────────────────────────────────────────────

def _user_repo(db: AsyncSession) -> UserRepository:
    return UserRepository(db)

def _org_repo(db: AsyncSession) -> OrganizationRepository:
    return OrganizationRepository(db)

def _org_member_repo(db: AsyncSession) -> OrganizationMemberRepository:
    return OrganizationMemberRepository(db)

def _document_repo(db: AsyncSession) -> DocumentRepository:
    return DocumentRepository(db)

def _document_file_repo(db: AsyncSession) -> DocumentFileRepository:
    return DocumentFileRepository(db)

def _vessel_repo(db: AsyncSession) -> VesselRepository:
    return VesselRepository(db)

def _vessel_identity_repo(db: AsyncSession) -> VesselIdentityRepository:
    return VesselIdentityRepository(db)

def _vessel_dimensions_repo(db: AsyncSession) -> VesselDimensionsRepository:
    return VesselDimensionsRepository(db)

def _vessel_certificate_repo(db: AsyncSession) -> VesselCertificateRepository:
    return VesselCertificateRepository(db)


# ── Public dependencies (what routers should import) ──────────────────────────

def get_user_service(
    db: AsyncSession = Depends(get_db_session),
) -> UserServiceProtocol:
    return UserService(
        db=db,
        users=_user_repo(db),
    )


def get_authed_user_service(
    db: AsyncSession = Depends(get_db_session),
    ctx: AuthContext = Depends(get_auth_context),
) -> UserServiceProtocol:
    return UserService(
        db=db,
        users=_user_repo(db),
        ctx=ctx,
    )


def get_organization_service(
    db: AsyncSession = Depends(get_db_session),
) -> OrganizationServiceProtocol:
    return OrganizationService(
        db=db,
        organizations=_org_repo(db),
        org_members=_org_member_repo(db),
    )


def get_authed_organization_service(
    db: AsyncSession = Depends(get_db_session),
    ctx: AuthContext = Depends(get_auth_context),
) -> OrganizationServiceProtocol:
    return OrganizationService(
        db=db,
        organizations=_org_repo(db),
        org_members=_org_member_repo(db),
        ctx=ctx,
    )


def get_document_service(
    db: AsyncSession = Depends(get_db_session),
    storage: StorageClient = Depends(get_storage_client),
    ctx: AuthContext = Depends(get_auth_context),
) -> DocumentServiceProtocol:
    return DocumentService(
        db=db,
        storage=storage,
        documents=_document_repo(db),
        files=_document_file_repo(db),
        users=_user_repo(db),
        orgs=_org_repo(db),
        ctx=ctx,
    )

def get_vessel_service(
    db: AsyncSession = Depends(get_db_session),
    ctx: AuthContext = Depends(get_auth_context),
) -> VesselServiceProtocol:
    return VesselService(
        db=db,
        vessels=_vessel_repo(db),
        identities=_vessel_identity_repo(db),
        dimensions=_vessel_dimensions_repo(db),
        certificates=_vessel_certificate_repo(db),
        users=_user_repo(db),
        orgs=_org_repo(db),
        ctx=ctx,
    )
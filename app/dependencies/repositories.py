"""
Repository dependency providers.

Each repository is instantiated once per request via FastAPI's dependency caching.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db import get_db_session

from app.domain.users.repository import UserRepository
from app.domain.users.repository.protocols import UserRepositoryProtocol

from app.domain.organization.repository import (
    OrganizationRepository,
    OrganizationMemberRepository,
)
from app.domain.organization.repository.protocols import (
    OrganizationRepositoryProtocol,
    OrganizationMemberRepositoryProtocol,
)

from app.domain.document.repository import (
    DocumentRepository,
    DocumentFileRepository,
)
from app.domain.document.repository.protocols import (
    DocumentRepositoryProtocol,
    DocumentFileRepositoryProtocol,
)


def get_user_repository(
    db: AsyncSession = Depends(get_db_session),
) -> UserRepositoryProtocol:
    """Provides UserRepository instance, cached per request."""
    return UserRepository(db)


def get_organization_repository(
    db: AsyncSession = Depends(get_db_session),
) -> OrganizationRepositoryProtocol:
    """Provides OrganizationRepository instance, cached per request."""
    return OrganizationRepository(db)


def get_organization_member_repository(
    db: AsyncSession = Depends(get_db_session),
) -> OrganizationMemberRepositoryProtocol:
    """Provides OrganizationMemberRepository instance, cached per request."""
    return OrganizationMemberRepository(db)


def get_document_repository(
    db: AsyncSession = Depends(get_db_session),
) -> DocumentRepositoryProtocol:
    """Provides DocumentRepository instance, cached per request."""
    return DocumentRepository(db)


def get_document_file_repository(
    db: AsyncSession = Depends(get_db_session),
) -> DocumentFileRepositoryProtocol:
    """Provides DocumentFileRepository instance, cached per request."""
    return DocumentFileRepository(db)
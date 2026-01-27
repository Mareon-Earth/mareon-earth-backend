from __future__ import annotations

from abc import abstractmethod

from app.domain._shared.repository import BaseRepository, CompositeKeyRepository
from app.domain._shared.types import OrganizationMemberId
from app.domain.organization.models import Organization, OrganizationMember

class OrganizationRepositoryProtocol(BaseRepository[Organization, str]):
    @abstractmethod
    async def get_by_clerk_id(self, clerk_org_id: str) -> Organization | None: ...

    @abstractmethod
    async def update(self, org: Organization) -> Organization: ...

class OrganizationMemberRepositoryProtocol(CompositeKeyRepository[OrganizationMember, OrganizationMemberId]):
    @abstractmethod
    async def get_by_id(self, id: OrganizationMemberId) -> OrganizationMember | None: ...

    @abstractmethod
    async def delete(self, id: OrganizationMemberId) -> None: ...

    @abstractmethod
    async def update(self, member: OrganizationMember) -> OrganizationMember: ...
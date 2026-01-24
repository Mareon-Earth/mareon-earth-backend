from typing import Protocol, Optional, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from app.domain.users import User, UserCreate, UserUpdate
    from app.domain.document import InitiateDocumentUploadRequest, InitiateDocumentUploadResponse

class UserServiceProtocol(Protocol):
    async def create_user(self, db: AsyncSession, payload: "UserCreate") -> "User": ...
    async def get_user(self, db: AsyncSession, user_id: str) -> "User": ...
    async def get_user_by_clerk_id(self, db: AsyncSession, clerk_user_id: str) -> "User": ...
    async def update_user(self, db: AsyncSession, clerk_user_id: str, payload: "UserUpdate") -> "User": ...
    async def delete_user(self, db: AsyncSession, clerk_user_id: str) -> None: ...

class DocumentServiceProtocol(Protocol):
    async def initiate_document_upload(
        self,
        db: AsyncSession,
        payload: "InitiateDocumentUploadRequest",
    ) -> "InitiateDocumentUploadResponse":
        ...

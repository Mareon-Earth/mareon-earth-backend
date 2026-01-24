from app.domain.protocols.services import UserServiceProtocol
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.domain.users import User, UserCreate, UserUpdate, UserNotFoundError, UserAlreadyExistsError
from app.domain.protocols.repositories import UserRepositoryProtocol
from app.core.auth.client import update_user_metadata

logger = logging.getLogger(__name__)


class UserService(UserServiceProtocol):
    """Service layer for User operations."""

    def __init__(self, user_repository: UserRepositoryProtocol):
        self.user_repository = user_repository

    async def get_or_create_from_clerk(self, db: AsyncSession, payload: UserCreate) -> User:
        existing_user = await self.user_repository.get_by_clerk_id(
            db, payload.clerk_user_id
        )
        if existing_user:
            return existing_user

        user = await self.user_repository.create(db, payload)
        await db.commit()
        await db.refresh(user)
        
        # Sync user_id back to Clerk user metadata
        await self._sync_user_metadata_to_clerk(user)
        
        return user

    async def create_user(self, db: AsyncSession, payload: UserCreate) -> User:
        """
        Create a new user.
        """
        existing_user = await self.user_repository.get_by_clerk_id(
            db, payload.clerk_user_id
        )
        if existing_user:
            raise UserAlreadyExistsError()
        
        user = await self.user_repository.create(db, payload)
        await db.commit()
        await db.refresh(user)
        
        # Sync user_id back to Clerk user metadata
        await self._sync_user_metadata_to_clerk(user)
        
        return user

    async def get_user(self, db: AsyncSession, user_id: str) -> User:
        """
        Retrieve a user by their ID.
        """
        user = await self.user_repository.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_user_by_clerk_id(self, db: AsyncSession, clerk_user_id: str) -> User:
        """
        Retrieve a user by their Clerk user ID.
        """
        user = await self.user_repository.get_by_clerk_id(db, clerk_user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def update_user(self, db: AsyncSession, clerk_user_id: str, payload: UserUpdate) -> User:
        """
        Update an existing user.
        """
        user = await self.user_repository.get_by_clerk_id(db, clerk_user_id)
        if not user:
            raise UserNotFoundError()

        updated_user = await self.user_repository.update(db, user, payload)
        await db.commit()
        await db.refresh(updated_user)
        return updated_user

    async def delete_user(self, db: AsyncSession, clerk_user_id: str) -> None:
        """
        Delete a user by their Clerk user ID.
        """
        user = await self.user_repository.get_by_clerk_id(db, clerk_user_id)
        if not user:
            raise UserNotFoundError()

        await self.user_repository.delete(db, user)
        await db.commit()

    async def _sync_user_metadata_to_clerk(self, user: User) -> None:
        """
        Sync user metadata back to Clerk as public metadata (available in JWT).
        This makes the internal user_id available in the JWT under public_metadata.
        """
        try:
            public_metadata = {
                "user_id": str(user.id),
            }
            
            await update_user_metadata(
                user.clerk_user_id,
                public_metadata=public_metadata
            )
            
            logger.info(f"Successfully synced user metadata to Clerk for user {user.clerk_user_id}")
        except Exception as e:
            logger.error(
                f"Failed to sync user metadata to Clerk for user {user.clerk_user_id}: {e}", 
                exc_info=True
            )
            # Don't raise - we don't want to fail user creation if Clerk sync fails
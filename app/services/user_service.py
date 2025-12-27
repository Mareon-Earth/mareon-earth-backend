from app.domain.protocols.services import UserServiceProtocol
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.models import User
from app.domain.users.schemas import UserCreate, UserUpdate
from app.domain.protocols.repositories import UserRepositoryProtocol
from app.domain.users.exceptions import UserNotFoundError, UserAlreadyExistsError


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
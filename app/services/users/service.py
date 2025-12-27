from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.repository import UserRepository
from app.domain.users.schemas import UserCreate, UserUpdate
from app.domain.users.exceptions import UserNotFoundError
from app.domain.users.models import User


class UserService:
    @staticmethod
    async def get_or_create_from_clerk(
        db: AsyncSession,
        payload: UserCreate,
    ) -> User:
        existing = await UserRepository.get_by_clerk_id(db, payload.clerk_user_id)
        if existing:
            return existing

        return await UserRepository.create(db, payload)

    @staticmethod
    async def update_user(
        db: AsyncSession,
        clerk_user_id: str,
        payload: UserUpdate,
    ) -> User:
        user = await UserRepository.get_by_clerk_id(db, clerk_user_id)
        if not user:
            # Domain exception – will be mapped to HTTP 404 by error handlers
            raise UserNotFoundError()

        return await UserRepository.update(db, user, payload)

    @staticmethod
    async def get_user(
        db: AsyncSession,
        user_id: str,
    ) -> User:
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()
        return user

    @staticmethod
    async def get_user_by_clerk_id(
        db: AsyncSession,
        clerk_user_id: str,
    ) -> User:
        user = await UserRepository.get_by_clerk_id(db, clerk_user_id)
        if not user:
            raise UserNotFoundError()
        return user

    @staticmethod
    async def delete_user(
        db: AsyncSession,
        clerk_user_id: str,
    ) -> None:
        """
        Delete user from database.
        Triggered by Clerk user.deleted webhook.
        """
        user = await UserRepository.get_by_clerk_id(db, clerk_user_id)
        if not user:
            raise UserNotFoundError()

        await UserRepository.delete(db, user)

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext, get_auth_context
from app.infrastructure.db import get_db_session

from app.domain.users.repository import UserRepository
from app.domain.users.service.protocols import UserServiceProtocol
from app.domain.users.service.user_service import UserService


def get_user_service(
    db: AsyncSession = Depends(get_db_session),
) -> UserServiceProtocol:
    return UserService(
        db=db,
        users=UserRepository(db),
    )


def get_authed_user_service(
    db: AsyncSession = Depends(get_db_session),
    ctx: AuthContext = Depends(get_auth_context),
) -> UserServiceProtocol:
    return UserService(
        db=db,
        users=UserRepository(db),
        ctx=ctx,
    )

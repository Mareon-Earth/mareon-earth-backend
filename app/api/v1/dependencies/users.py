from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext, get_auth_context
from app.infrastructure.db import get_db_session
from app.domain.users.service.protocols import UserServiceProtocol
from app.domain.users.dependencies import build_user_service

def get_user_service(
    db: AsyncSession = Depends(get_db_session),
) -> UserServiceProtocol:
    return build_user_service(db=db)

def get_authed_user_service(
    db: AsyncSession = Depends(get_db_session),
    ctx: AuthContext = Depends(get_auth_context),
) -> UserServiceProtocol:
    return build_user_service(db=db, ctx=ctx)

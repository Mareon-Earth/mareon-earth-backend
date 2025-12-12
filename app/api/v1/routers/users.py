from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth import get_auth_context, AuthContext
from app.infrastructure.database import get_db_session
from app.services.users import UserService
from app.domain.users.schemas import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_me(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Return the current user based on the authenticated Clerk user.
    """
    user = await UserService.get_user_by_clerk_id(db, ctx.user_id)
    return user


@router.patch("/me", response_model=UserRead)
async def update_me(
    payload: UserUpdate,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Update current user's profile.
    """
    user = await UserService.update_user(db, ctx.user_id, payload)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Fetch a user by internal Mareon user ID.
    """
    user = await UserService.get_user(db, user_id)
    return user

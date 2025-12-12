from fastapi import APIRouter, Depends
from app.core.auth.auth import get_auth_context, AuthContext

router = APIRouter(tags=["auth-test"])

@router.get("/me")
async def read_me(ctx: AuthContext = Depends(get_auth_context)):
    return {"user_id": ctx.user_id}

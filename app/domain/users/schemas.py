from pydantic import BaseModel
from typing import Optional
from app.domain._shared.types import DateTime


class UserBase(BaseModel):
    clerk_user_id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    image_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating new user entries (usually from Clerk webhook)."""
    pass


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    id: str
    is_active: bool
    created_at: DateTime
    updated_at: DateTime

    class Config:
        from_attributes = True

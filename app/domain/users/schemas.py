from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    last_login_at: Optional[datetime] = None


class UserRead(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

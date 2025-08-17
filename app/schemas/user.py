import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

    @validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v.strip():
            raise ValueError('Username cannot be empty or whitespace')
        if len(v) > 50:
            raise ValueError('Username must be 50 characters or less')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

    @validator('username')
    @classmethod
    def validate_username(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Username cannot be empty or whitespace')
            if len(v) > 50:
                raise ValueError('Username must be 50 characters or less')
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('Username can only contain letters, numbers, and underscores')
        return v


class UserStatusUpdate(BaseModel):
    """Schema for updating user status by superuser/admin."""
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_superuser: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool = True
    is_admin: bool = False
    is_superuser: bool = False

    class Config:
        from_attributes = True

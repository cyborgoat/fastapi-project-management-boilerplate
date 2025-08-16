from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr

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


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

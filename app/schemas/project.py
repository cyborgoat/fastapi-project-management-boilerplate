from typing import Optional

from pydantic import BaseModel, Field, validator


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    @validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Project title cannot be empty or whitespace')
        if len(v) > 200:
            raise ValueError('Project title must be 200 characters or less')
        return v

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectInDBBase(ProjectBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class Project(ProjectInDBBase):
    pass

class ProjectInDB(ProjectInDBBase):
    pass

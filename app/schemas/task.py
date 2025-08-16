from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, validator


class TaskBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: bool = Field(default=False, alias="completed")

    @validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Task title cannot be empty or whitespace')
        if len(v) > 200:
            raise ValueError('Task title must be 200 characters or less')
        return v

class TaskCreate(TaskBase):
    project_id: int
    assignee_id: Optional[int] = None

class TaskUpdate(TaskBase):
    pass

class TaskInDBBase(TaskBase):
    id: int
    project_id: int
    assignee_id: Optional[int] = None

    class Config:
        from_attributes = True

class Task(TaskInDBBase):
    pass

class TaskInDB(TaskInDBBase):
    pass

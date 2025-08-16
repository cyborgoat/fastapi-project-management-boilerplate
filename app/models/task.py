from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    due_date = Column(DateTime)
    is_completed = Column(Boolean(), default=False)
    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="tasks")
    assignee_id = Column(Integer, ForeignKey("user.id"))
    assignee = relationship("User", back_populates="tasks")

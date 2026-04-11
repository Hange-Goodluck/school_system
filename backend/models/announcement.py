from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from backend.models.base import TimestampMixin
from backend.models.user import User

class Announcement(TimestampMixin, SQLModel, table=True):
    __tablename__ = "announcements"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    content: str
    is_published: bool = Field(default=True)
    published_at: Optional[datetime] = Field(default=None)

    # Foreign key to user who created it
    author_id: int = Field(foreign_key="users.id")

    # Relationship
    author: User = Relationship(back_populates="announcements")
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from backend.models.enums import UserRole
from backend.models.base import TimestampMixin

if TYPE_CHECKING:
    from backend.models.student import Student
    from backend.models.teacher import Teacher
    from backend.models.admin import Admin
    from backend.models.announcement import Announcement

class User(TimestampMixin, SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)

    full_name: str
    email: str = Field(index=True, unique=True)

    hashed_password: str

    role: UserRole = Field(default=UserRole.student)

    is_active: bool = Field(default=True)

    # Relationships
    student_profile: Optional["Student"] = Relationship(back_populates="user")
    teacher_profile: Optional["Teacher"] = Relationship(back_populates="user")
    admin_profile: Optional["Admin"] = Relationship(back_populates="user")
    announcements: List["Announcement"] = Relationship(back_populates="author")
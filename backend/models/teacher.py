from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import date
from backend.models.base import TimestampMixin

if TYPE_CHECKING:
    from backend.models.user import User
    from backend.models.student import Student


class Teacher(TimestampMixin, SQLModel, table=True):
    __tablename__ = "teachers"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    employee_id: str = Field(unique=True, index=True)  # e.g., "TCH2024001"
    department: str  # e.g., "Mathematics", "Science"
    subjects: str  # Comma-separated subjects they teach
    hire_date: date = Field(default_factory=date.today)

    # Relationship to the base user account
    user: Optional["User"] = Relationship(back_populates="teacher_profile")
    students: List["Student"] = Relationship(back_populates="teacher")
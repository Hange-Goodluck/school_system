from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from backend.models.base import TimestampMixin

if TYPE_CHECKING:
    from backend.models.student import Student

class StudentSubject(TimestampMixin, SQLModel, table=True):
    __tablename__ = "student_subjects"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    subject: str
    status: str = Field(default="enrolled")  # enrolled, completed, withdrawn

    student: "Student" = Relationship(back_populates="subjects")

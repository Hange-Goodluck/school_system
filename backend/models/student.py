from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date
from backend.models.base import TimestampMixin
from backend.models.user import User

if TYPE_CHECKING:
    from backend.models.student_score import StudentScore
    from backend.models.student_subject import StudentSubject
    from backend.models.attendance import Attendance

class Student(TimestampMixin, SQLModel, table=True):
    __tablename__ = "students"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    student_id: str = Field(unique=True, index=True)  # e.g., "STU2024001"
    grade_level: str = Field(default="JSS1")  # JSS1, JSS2, JSS3, SS1, SS2, SS3
    date_of_birth: date
    enrollment_date: date = Field(default_factory=lambda: date.today())
    teacher_id: Optional[int] = Field(default=None, foreign_key="teachers.id")

    # Relationships
    user: User = Relationship(back_populates="student_profile")
    teacher: Optional["Teacher"] = Relationship(back_populates="students")
    scores: List["StudentScore"] = Relationship(back_populates="student")
    subjects: List["StudentSubject"] = Relationship(back_populates="student")
    attendance_records: List["Attendance"] = Relationship(back_populates="student")

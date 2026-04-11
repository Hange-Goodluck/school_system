from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date
from backend.models.base import TimestampMixin

if TYPE_CHECKING:
    from backend.models.student import Student

class Attendance(TimestampMixin, SQLModel, table=True):
    __tablename__ = "attendance"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    subject: str  # The subject for this attendance record
    attendance_date: date
    status: str = Field(default="present")  # present, absent, late, excused
    notes: Optional[str] = None  # Optional notes about the absence/lateness

    student: Optional["Student"] = Relationship(back_populates="attendance_records")
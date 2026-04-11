from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from backend.models.base import TimestampMixin
from backend.models.student import Student

class StudentScore(TimestampMixin, SQLModel, table=True):
    __tablename__ = "student_scores"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    subject: str
    score: float
    term: str = Field(default="2026")

    student: Student = Relationship(back_populates="scores")

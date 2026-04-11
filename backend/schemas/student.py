from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class StudentCreate(BaseModel):
    student_id: str
    grade_level: str
    date_of_birth: date
    enrollment_date: Optional[date] = None
    teacher_id: Optional[int] = None

class StudentUpdate(BaseModel):
    student_id: Optional[str] = None
    grade_level: Optional[str] = None
    date_of_birth: Optional[date] = None
    enrollment_date: Optional[date] = None
    teacher_id: Optional[int] = None

class StudentResponse(BaseModel):
    id: int
    user_id: int
    student_id: str
    grade_level: str
    date_of_birth: date
    enrollment_date: date
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
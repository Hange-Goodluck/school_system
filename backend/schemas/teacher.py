from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class TeacherCreate(BaseModel):
    user_id: int
    employee_id: str
    department: str
    subjects: str

class TeacherResponse(BaseModel):
    id: int
    user_id: int
    employee_id: str
    department: str
    subjects: str
    hire_date: date
    user_full_name: Optional[str] = None
    user_email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StudentSubjectCreate(BaseModel):
    student_id: int
    subject: str
    status: Optional[str] = "enrolled"

class StudentSubjectResponse(BaseModel):
    id: int
    student_id: int
    subject: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

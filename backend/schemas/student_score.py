from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StudentScoreCreate(BaseModel):
    student_id: int
    subject: str
    score: float
    term: Optional[str] = "2026"

class StudentScoreResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str]
    subject: str
    score: float
    term: str
    created_at: datetime
    updated_at: Optional[datetime]

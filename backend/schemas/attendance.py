from pydantic import BaseModel
from datetime import date
from typing import Optional

class AttendanceCreate(BaseModel):
    student_id: int
    subject: str
    attendance_date: date
    status: str = "present"
    notes: Optional[str] = None

class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    subject: str
    attendance_date: date
    status: str
    notes: Optional[str]
    created_at: date
    updated_at: Optional[date]

class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class BulkAttendanceCreate(BaseModel):
    class_name: str
    subject: str
    attendance_date: date
    attendance_records: dict[int, str]  # student_id -> status

class WeeklyAttendanceReport(BaseModel):
    student_id: int
    student_name: str
    week_start: date
    week_end: date
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    excused_days: int
    attendance_percentage: float
    subjects: dict[str, int]  # subject -> attendance count
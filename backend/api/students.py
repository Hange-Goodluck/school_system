from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from backend.db.database import get_db
from backend.models import Student, User
from backend.models.enums import UserRole
from backend.schemas.student import StudentCreate, StudentResponse
from backend.core.dependencies import get_current_user

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=StudentResponse)
def create_student(
    student_data: StudentCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Check if user already has a student profile
    existing = session.exec(select(Student).where(Student.user_id == current_user.id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student profile already exists")

    student = Student(
        user_id=current_user.id,
        student_id=student_data.student_id,
        grade_level=student_data.grade_level,
        date_of_birth=student_data.date_of_birth,
        enrollment_date=student_data.enrollment_date
    )

    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@router.get("/me", response_model=StudentResponse)
def get_my_student_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    student = session.exec(select(Student).where(Student.user_id == current_user.id)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student

@router.get("/", response_model=List[StudentResponse])
def list_students(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins and teachers can list all students
    if current_user.role not in [UserRole.admin, UserRole.teacher]:
        raise HTTPException(status_code=403, detail="Not authorized")

    students = session.exec(select(Student)).all()
    return students
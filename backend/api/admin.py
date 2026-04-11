from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from backend.db.database import get_db
from backend.models import Student, Announcement, User, StudentScore, StudentSubject, Attendance, Teacher
from backend.models.enums import UserRole
from backend.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from backend.schemas.announcement import AnnouncementCreate, AnnouncementResponse, AnnouncementUpdate
from backend.schemas.student_score import StudentScoreCreate, StudentScoreResponse
from backend.schemas.student_subject import StudentSubjectCreate, StudentSubjectResponse
from backend.schemas.attendance import AttendanceCreate, AttendanceResponse, AttendanceUpdate, BulkAttendanceCreate, WeeklyAttendanceReport
from backend.schemas.teacher import TeacherCreate, TeacherResponse
from backend.core.dependencies import get_current_user

class StudentCreateWithUser(BaseModel):
    user_id: int
    student_id: str
    grade_level: str
    date_of_birth: date
    enrollment_date: Optional[date] = None

router = APIRouter(prefix="/admin", tags=["Admin"])

from backend.schemas.auth import UserCreate, UserResponse
from backend.core.security import hash_password

# User Management Endpoints

@router.post("/users", response_model=UserResponse)
@router.post("/users/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can create users
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/students", response_model=StudentResponse)
@router.post("/students/", response_model=StudentResponse)
def create_student(
    student_data: StudentCreateWithUser,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can create students
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if user exists
    user = session.get(User, student_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user already has a student profile
    existing = session.exec(select(Student).where(Student.user_id == student_data.user_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student profile already exists for this user")

    student = Student(
        user_id=student_data.user_id,
        student_id=student_data.student_id,
        grade_level=student_data.grade_level,
        date_of_birth=student_data.date_of_birth,
        enrollment_date=student_data.enrollment_date
    )

    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@router.get("/students", response_model=List[StudentResponse])
@router.get("/students/", response_model=List[StudentResponse])
def list_all_students(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can list all students
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    students = session.exec(select(Student)).all()
    return students

@router.post("/teachers", response_model=TeacherResponse)
@router.post("/teachers/", response_model=TeacherResponse)
def create_teacher(
    teacher_data: TeacherCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = session.get(User, teacher_data.user_id)
    if not user or user.role != UserRole.teacher:
        raise HTTPException(status_code=404, detail="Teacher user not found or not a teacher role")

    existing = session.exec(select(Teacher).where(Teacher.user_id == teacher_data.user_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Teacher profile already exists for this user")

    teacher = Teacher(
        user_id=teacher_data.user_id,
        employee_id=teacher_data.employee_id,
        department=teacher_data.department,
        subjects=teacher_data.subjects
    )

    session.add(teacher)
    session.commit()
    session.refresh(teacher)

    return {
        "id": teacher.id,
        "user_id": teacher.user_id,
        "employee_id": teacher.employee_id,
        "department": teacher.department,
        "subjects": teacher.subjects,
        "hire_date": teacher.hire_date,
        "user_full_name": teacher.user.full_name if teacher.user else None,
        "user_email": teacher.user.email if teacher.user else None,
        "created_at": teacher.created_at,
        "updated_at": teacher.updated_at,
    }

@router.get("/teachers", response_model=List[TeacherResponse])
@router.get("/teachers/", response_model=List[TeacherResponse])
def list_teachers(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    teachers = session.exec(select(Teacher)).all()
    return [
        {
            "id": teacher.id,
            "user_id": teacher.user_id,
            "employee_id": teacher.employee_id,
            "department": teacher.department,
            "subjects": teacher.subjects,
            "hire_date": teacher.hire_date,
            "user_full_name": teacher.user.full_name if teacher.user else None,
            "user_email": teacher.user.email if teacher.user else None,
            "created_at": teacher.created_at,
            "updated_at": teacher.updated_at,
        }
        for teacher in teachers
    ]

@router.get("/teachers/me", response_model=dict)
def get_my_teacher_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role != UserRole.teacher:
        raise HTTPException(status_code=403, detail="Not authorized")

    teacher = session.exec(select(Teacher).where(Teacher.user_id == current_user.id)).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    students = session.exec(select(Student).where(Student.teacher_id == teacher.id)).all()
    assigned_students = [
        {
            "id": student.id,
            "student_id": student.student_id,
            "student_name": student.user.full_name if student.user else None,
            "grade_level": student.grade_level,
            "date_of_birth": student.date_of_birth,
            "enrollment_date": student.enrollment_date,
            "teacher_id": student.teacher_id
        }
        for student in students
    ]

    return {
        "teacher_id": teacher.id,
        "user_id": teacher.user_id,
        "employee_id": teacher.employee_id,
        "department": teacher.department,
        "subjects": teacher.subjects,
        "hire_date": teacher.hire_date,
        "user_full_name": teacher.user.full_name if teacher.user else None,
        "user_email": teacher.user.email if teacher.user else None,
        "assigned_students": assigned_students,
        "student_count": len(assigned_students)
    }

@router.put("/students/{student_id}/assign-teacher", response_model=StudentResponse)
def assign_student_teacher(
    student_id: int,
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    teacher = session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    student.teacher_id = teacher.id
    session.add(student)
    session.commit()
    session.refresh(student)

    return {
        "id": student.id,
        "user_id": student.user_id,
        "student_id": student.student_id,
        "grade_level": student.grade_level,
        "date_of_birth": student.date_of_birth,
        "enrollment_date": student.enrollment_date,
        "teacher_id": student.teacher_id,
        "teacher_name": teacher.user.full_name if teacher.user else None,
        "created_at": student.created_at,
        "updated_at": student.updated_at,
    }

@router.get("/teachers/{teacher_id}/students", response_model=List[StudentResponse])
def list_students_for_teacher(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.admin, UserRole.teacher]:
        raise HTTPException(status_code=403, detail="Not authorized")

    teacher = session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if current_user.role == UserRole.teacher and teacher.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    students = session.exec(select(Student).where(Student.teacher_id == teacher.id)).all()
    return [
        {
            "id": student.id,
            "user_id": student.user_id,
            "student_id": student.student_id,
            "grade_level": student.grade_level,
            "date_of_birth": student.date_of_birth,
            "enrollment_date": student.enrollment_date,
            "teacher_id": student.teacher_id,
            "teacher_name": teacher.user.full_name if teacher.user else None,
            "created_at": student.created_at,
            "updated_at": student.updated_at,
        }
        for student in students
    ]

@router.post("/scores", response_model=StudentScoreResponse)
@router.post("/scores/", response_model=StudentScoreResponse)
def create_student_score(
    score_data: StudentScoreCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    student = session.get(Student, score_data.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    score = StudentScore(
        student_id=score_data.student_id,
        subject=score_data.subject,
        score=score_data.score,
        term=score_data.term or "2026"
    )

    session.add(score)
    session.commit()
    session.refresh(score)

    student_name = None
    if student and student.user:
        student_name = student.user.full_name

    return {
        "id": score.id,
        "student_id": score.student_id,
        "student_name": student_name,
        "subject": score.subject,
        "score": score.score,
        "term": score.term,
        "created_at": score.created_at,
        "updated_at": score.updated_at,
    }

@router.get("/scores", response_model=List[StudentScoreResponse])
def list_all_student_scores(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    scores = session.exec(select(StudentScore)).all()
    result = []
    for score in scores:
        student = session.get(Student, score.student_id)
        student_name = None
        if student and student.user:
            student_name = student.user.full_name
        result.append({
            "id": score.id,
            "student_id": score.student_id,
            "student_name": student_name,
            "subject": score.subject,
            "score": score.score,
            "term": score.term,
            "created_at": score.created_at,
            "updated_at": score.updated_at,
        })
    return result

@router.get("/students/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can access student details
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can update students
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Update fields
    update_data = student_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)

    session.commit()
    session.refresh(student)
    return student

@router.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can delete students
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    session.delete(student)
    session.commit()
@router.get("/users", response_model=List[UserResponse])
@router.get("/users/", response_model=List[UserResponse])
def list_all_users(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can list all users
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    users = session.exec(select(User)).all()
    return users

# Announcement Management Endpoints

@router.post("/announcements", response_model=AnnouncementResponse)
@router.post("/announcements/", response_model=AnnouncementResponse)
def create_announcement(
    announcement_data: AnnouncementCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can create announcements
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    announcement = Announcement(
        title=announcement_data.title,
        content=announcement_data.content,
        is_published=announcement_data.is_published,
        author_id=current_user.id
    )

    session.add(announcement)
    session.commit()
    session.refresh(announcement)
    return announcement

@router.get("/announcements", response_model=List[AnnouncementResponse])
@router.get("/announcements/", response_model=List[AnnouncementResponse])
def list_all_announcements(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can list all announcements (including unpublished)
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    announcements = session.exec(select(Announcement)).all()
    return announcements

@router.get("/announcements/{announcement_id}", response_model=AnnouncementResponse)
def get_announcement(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can access announcement details
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    announcement = session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement

@router.put("/announcements/{announcement_id}", response_model=AnnouncementResponse)
def update_announcement(
    announcement_id: int,
    announcement_data: AnnouncementUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can update announcements
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    announcement = session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    # Update fields
    update_data = announcement_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(announcement, key, value)

    session.commit()
    session.refresh(announcement)
    return announcement

@router.delete("/announcements/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can delete announcements
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    announcement = session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    session.delete(announcement)
    session.commit()
    return {"message": "Announcement deleted successfully"}
# Student Subject Management Endpoints

# 15 Core Nigerian Subjects
NIGERIAN_SUBJECTS = [
    "English Language",
    "Mathematics",
    "Biology",
    "Chemistry",
    "Physics",
    "History",
    "Geography",
    "Civic Education",
    "Literature in English",
    "Computer Science",
    "Agricultural Science",
    "Government",
    "Physical Education",
    "Economics",
]

@router.post("/student-subjects", response_model=StudentSubjectResponse)
@router.post("/student-subjects/", response_model=StudentSubjectResponse)
def create_student_subject(
    subject_data: StudentSubjectCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can create student-subject enrollments
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if student exists
    student = session.get(Student, subject_data.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check if enrollment already exists
    existing = session.exec(
        select(StudentSubject).where(
            (StudentSubject.student_id == subject_data.student_id) &
            (StudentSubject.subject == subject_data.subject)
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Subject already enrolled for this student")

    student_subject = StudentSubject(
        student_id=subject_data.student_id,
        subject=subject_data.subject,
        status=subject_data.status or "enrolled"
    )

    session.add(student_subject)
    session.commit()
    session.refresh(student_subject)
    return student_subject

@router.get("/student-subjects", response_model=List[StudentSubjectResponse])
@router.get("/student-subjects/", response_model=List[StudentSubjectResponse])
def list_student_subjects(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can list student-subject enrollments
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    subjects = session.exec(select(StudentSubject)).all()
    return subjects

@router.get("/student-subjects/by-class/{class_name}", response_model=List[StudentSubjectResponse])
def get_student_subjects_by_class(
    class_name: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can access
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get all students in this class
    students = session.exec(
        select(Student).where(Student.grade_level == class_name)
    ).all()

    student_ids = [s.id for s in students]

    # Get all subjects for these students
    subjects = session.exec(
        select(StudentSubject).where(StudentSubject.student_id.in_(student_ids))
    ).all()

    return subjects

@router.delete("/student-subjects/{subject_id}")
def delete_student_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can delete enrollments
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    subject = session.get(StudentSubject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject enrollment not found")

    session.delete(subject)
    session.commit()
    return {"message": "Subject enrollment deleted successfully"}

# Student Register View - Gets all students with subjects grouped by class
from pydantic import BaseModel as PydanticBaseModel

class StudentWithSubjectsSchema(PydanticBaseModel):
    student_id: int
    student_name: str
    grade_level: str
    subjects: List[str]

class StudentRegisterSchema(PydanticBaseModel):
    class_name: str
    students: List[StudentWithSubjectsSchema]

@router.get("/student-register", response_model=dict)
@router.get("/student-register/", response_model=dict)
def get_student_register(
    grade_level: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only admins can access
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get all students, optionally filtered by grade_level
    if grade_level:
        all_students = session.exec(
            select(Student).where(Student.grade_level == grade_level)
        ).all()
    else:
        all_students = session.exec(select(Student)).all()

    # Group by class
    students_by_class = {}
    
    for student in all_students:
        grade = student.grade_level or "Unknown"
        
        if grade not in students_by_class:
            students_by_class[grade] = []
        
        # Calculate age from DOB
        today = datetime.now().date()
        age = today.year - student.date_of_birth.year - (
            (today.month, today.day) < (student.date_of_birth.month, student.date_of_birth.day)
        )
        
        # Get subjects for this student
        student_subjects = session.exec(
            select(StudentSubject).where(StudentSubject.student_id == student.id)
        ).all()
        
        subject_names = [ss.subject for ss in student_subjects]
        
        students_by_class[grade].append({
            "id": student.id,
            "student_id": student.student_id,
            "student_name": student.user.full_name if student.user else f"Student {student.id}",
            "email": student.user.email if student.user else "N/A",
            "grade_level": grade,
            "date_of_birth": student.date_of_birth.isoformat(),
            "age": age,
            "enrollment_date": student.enrollment_date.isoformat(),
            "subjects": subject_names,
            "subject_count": len(subject_names)
        })
    
    # Get all unique classes
    all_classes = session.exec(select(Student.grade_level).distinct()).all()
    available_classes = sorted(list(set([c for c in all_classes if c])))
    
    return {
        "classes": students_by_class,
        "available_classes": available_classes,
        "available_subjects": NIGERIAN_SUBJECTS,
        "total_students": len(all_students),
        "filtered_by_class": grade_level
    }

# Attendance Management Endpoints

@router.post("/attendance", response_model=AttendanceResponse)
@router.post("/attendance/", response_model=AttendanceResponse)
def create_attendance(
    attendance_data: AttendanceCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.admin, UserRole.teacher]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if student exists
    student = session.get(Student, attendance_data.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.role == UserRole.teacher:
        teacher = session.exec(select(Teacher).where(Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher profile not found")
        if student.teacher_id != teacher.id:
            raise HTTPException(status_code=403, detail="Not authorized to mark attendance for this student")

    # Check if attendance record already exists for this student, subject, and date
    existing = session.exec(
        select(Attendance).where(
            (Attendance.student_id == attendance_data.student_id) &
            (Attendance.subject == attendance_data.subject) &
            (Attendance.attendance_date == attendance_data.attendance_date)
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Attendance record already exists for this student, subject, and date")

    attendance = Attendance(
        student_id=attendance_data.student_id,
        subject=attendance_data.subject,
        attendance_date=attendance_data.attendance_date,
        status=attendance_data.status,
        notes=attendance_data.notes
    )

    session.add(attendance)
    session.commit()
    session.refresh(attendance)
    return attendance

@router.post("/attendance/bulk", response_model=dict)
@router.post("/attendance/bulk/", response_model=dict)
def create_bulk_attendance(
    bulk_data: BulkAttendanceCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.admin, UserRole.teacher]:
        raise HTTPException(status_code=403, detail="Not authorized")

    teacher = None
    teacher_student_ids = []
    if current_user.role == UserRole.teacher:
        teacher = session.exec(select(Teacher).where(Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher profile not found")
        teacher_student_ids = [s.id for s in session.exec(select(Student.id).where(Student.teacher_id == teacher.id)).all()]

    if bulk_data.student_ids:
        students = session.exec(select(Student).where(Student.id.in_(bulk_data.student_ids))).all()
    elif bulk_data.class_name:
        students = session.exec(select(Student).where(Student.grade_level == bulk_data.class_name)).all()
    else:
        if current_user.role == UserRole.teacher:
            students = session.exec(select(Student).where(Student.teacher_id == teacher.id)).all()
        else:
            students = session.exec(select(Student)).all()

    if not students:
        raise HTTPException(status_code=404, detail="No students found for attendance assignment")

    created_records = []
    skipped_records = []

    for student in students:
        if current_user.role == UserRole.teacher and student.id not in teacher_student_ids:
            continue

        status = bulk_data.attendance_records.get(student.id, "present")

        existing = session.exec(
            select(Attendance).where(
                (Attendance.student_id == student.id) &
                (Attendance.subject == bulk_data.subject) &
                (Attendance.attendance_date == bulk_data.attendance_date)
            )
        ).first()

        if existing:
            skipped_records.append({
                "student_id": student.id,
                "student_name": student.user.full_name if student.user else f"Student {student.id}",
                "reason": "Record already exists"
            })
            continue

        attendance = Attendance(
            student_id=student.id,
            subject=bulk_data.subject,
            attendance_date=bulk_data.attendance_date,
            status=status
        )

        session.add(attendance)
        created_records.append({
            "student_id": student.id,
            "student_name": student.user.full_name if student.user else f"Student {student.id}",
            "status": status
        })

    session.commit()

    return {
        "message": f"Created {len(created_records)} attendance records, skipped {len(skipped_records)} existing records",
        "created": created_records,
        "skipped": skipped_records,
        "class": bulk_data.class_name,
        "subject": bulk_data.subject,
        "date": bulk_data.attendance_date
    }

@router.get("/attendance", response_model=List[AttendanceResponse])
@router.get("/attendance/", response_model=List[AttendanceResponse])
def list_attendance(
    student_id: Optional[int] = Query(None),
    subject: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.admin, UserRole.teacher]:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(Attendance)

    if student_id:
        query = query.where(Attendance.student_id == student_id)

    if subject:
        query = query.where(Attendance.subject == subject)

    if class_name:
        # Join with Student to filter by class
        query = query.join(Student).where(Student.grade_level == class_name)

    if current_user.role == UserRole.teacher:
        teacher = session.exec(select(Teacher).where(Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher profile not found")
        student_ids = [s.id for s in session.exec(select(Student.id).where(Student.teacher_id == teacher.id)).all()]
        query = query.where(Attendance.student_id.in_(student_ids))

    if start_date:
        query = query.where(Attendance.attendance_date >= start_date)

    if end_date:
        query = query.where(Attendance.attendance_date <= end_date)

    attendance_records = session.exec(query).all()
    return attendance_records

@router.get("/attendance/reports/weekly", response_model=dict)
@router.get("/attendance/reports/weekly/", response_model=dict)
def get_weekly_attendance_report(
    week_start: date,
    class_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.admin, UserRole.teacher]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Calculate week end (7 days from start)
    from datetime import timedelta
    week_end = week_start + timedelta(days=6)

    # Get relevant students
    if current_user.role == UserRole.teacher:
        teacher = session.exec(select(Teacher).where(Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher profile not found")
        student_query = select(Student).where(Student.teacher_id == teacher.id)
        if class_name:
            student_query = student_query.where(Student.grade_level == class_name)
    else:
        student_query = select(Student)
        if class_name:
            student_query = student_query.where(Student.grade_level == class_name)

    students = session.exec(student_query).all()

    report_data = []

    for student in students:
        # Get attendance records for this student in the week
        attendance_records = session.exec(
            select(Attendance).where(
                (Attendance.student_id == student.id) &
                (Attendance.attendance_date >= week_start) &
                (Attendance.attendance_date <= week_end)
            )
        ).all()

        # Calculate attendance statistics
        total_days = len(attendance_records)
        present_days = sum(1 for r in attendance_records if r.status == "present")
        absent_days = sum(1 for r in attendance_records if r.status == "absent")
        late_days = sum(1 for r in attendance_records if r.status == "late")
        excused_days = sum(1 for r in attendance_records if r.status == "excused")

        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

        # Group by subject
        subject_stats = {}
        for record in attendance_records:
            if record.subject not in subject_stats:
                subject_stats[record.subject] = 0
            if record.status == "present":
                subject_stats[record.subject] += 1

        report_data.append({
            "student_id": student.id,
            "student_name": student.user.full_name if student.user else f"Student {student.id}",
            "grade_level": student.grade_level,
            "week_start": week_start,
            "week_end": week_end,
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "late_days": late_days,
            "excused_days": excused_days,
            "attendance_percentage": round(attendance_percentage, 1),
            "subjects": subject_stats
        })

    # Sort by attendance percentage (lowest first for attention)
    report_data.sort(key=lambda x: x["attendance_percentage"])

    return {
        "week_start": week_start,
        "week_end": week_end,
        "class_filter": class_name,
        "total_students": len(report_data),
        "reports": report_data,
        "summary": {
            "average_attendance": round(sum(r["attendance_percentage"] for r in report_data) / len(report_data), 1) if report_data else 0,
            "students_with_low_attendance": len([r for r in report_data if r["attendance_percentage"] < 80]),
            "perfect_attendance": len([r for r in report_data if r["attendance_percentage"] == 100])
        }
    }
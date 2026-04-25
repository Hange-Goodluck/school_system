from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from backend.core.config import settings
from backend.db.database import engine
from backend.models import User, Announcement, Student, StudentSubject
from backend.models.enums import UserRole
from backend.api import auth
from backend.api.public import router as public_router
from backend.api.students import router as students_router
from backend.api.announcements import router as announcements_router
from backend.api.admin import router as admin_router
from typing import Optional
from datetime import date

app = FastAPI(
    title="School Management System",
    description="A comprehensive school management system with FastAPI backend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="backend/templates")

@app.get("/")
def root():
    return {
        "message": "School Management System API",
        "docs": "/docs",
        "frontend": "/home"
    }

@app.get("/home")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("log.html", {"request": request})

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard/student")
def student_dashboard(request: Request):
    return templates.TemplateResponse("student_dashboard.html", {"request": request})

@app.get("/dashboard/teacher")
def teacher_dashboard(request: Request):
    return templates.TemplateResponse("teacher_dasboard.html", {"request": request})

@app.get("/dashboard/admin")
def admin_dashboard(request: Request):
    with Session(engine) as session:
        student_count = len(session.exec(select(User).where(User.role == UserRole.student)).all())
        teacher_count = len(session.exec(select(User).where(User.role == UserRole.teacher)).all())
        announcement_count = len(session.exec(select(Announcement)).all())

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "student_count": student_count,
            "teacher_count": teacher_count,
            "announcement_count": announcement_count,
        },
    )

def build_student_register_data(grade_level: Optional[str] = None):
    with Session(engine) as session:
        if grade_level:
            students = session.exec(
                select(Student).where(Student.grade_level == grade_level)
            ).all()
        else:
            students = session.exec(select(Student)).all()

        students_by_class = {}
        for student in students:
            grade = student.grade_level or "Unknown"
            if grade not in students_by_class:
                students_by_class[grade] = []

            today = date.today()
            age = today.year - student.date_of_birth.year - (
                (today.month, today.day) < (student.date_of_birth.month, student.date_of_birth.day)
            )

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
                "date_of_birth": student.date_of_birth,
                "age": age,
                "enrollment_date": student.enrollment_date,
                "subjects": subject_names,
                "subject_count": len(subject_names),
            })

        all_classes = session.exec(select(Student.grade_level).distinct()).all()
        available_classes = sorted(list({c for c in all_classes if c}))

    return students_by_class, available_classes, len(students)

@app.get("/student-register")
def student_register_page(request: Request, grade_level: Optional[str] = None):
    students_by_class, available_classes, total_students = build_student_register_data(grade_level)
    return templates.TemplateResponse(
        "student_register.html",
        {
            "request": request,
            "students_by_class": students_by_class,
            "available_classes": available_classes,
            "total_students": total_students,
            "selected_class": grade_level,
        },
    )

@app.get("/attendance")
def attendance_page(request: Request):
    return templates.TemplateResponse("attendance.html", {"request": request})

# Include routers
app.include_router(auth.router)
app.include_router(public_router)
app.include_router(students_router)
app.include_router(announcements_router)
app.include_router(admin_router)


















































































































































































































































































#with the new one in chat.py, then test with the frontend to make sure it works.then run alembic to create the new database schema with the updated user model.#Also make sure to update the frontend script to handle the new message format if necessary.
# # Then, proceed to implement any additional features or fixes as needed.

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from backend.core.config import settings
from backend.db.database import engine
from backend.models import User, Announcement
from backend.models.enums import UserRole
from backend.api import auth
from backend.api.public import router as public_router
from backend.api.students import router as students_router
from backend.api.announcements import router as announcements_router
from backend.api.admin import router as admin_router

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

@app.get("/student-register")
def student_register_page(request: Request):
    return templates.TemplateResponse("student_register.html", {"request": request})

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

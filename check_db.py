#!/usr/bin/env python3
"""
Check database state
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, select
from backend.db.database import engine
from backend.models import Student, User, StudentSubject

def check_database():
    with Session(engine) as session:
        students = session.exec(select(Student)).all()
        users = session.exec(select(User)).all()
        subjects = session.exec(select(StudentSubject)).all()

        print(f"Total users: {len(users)}")
        print(f"Total students: {len(students)}")
        print(f"Total student-subject enrollments: {len(subjects)}")

        print("\nStudents:")
        for student in students:
            user_name = student.user.full_name if student.user else "No user linked"
            print(f"  - {user_name} (ID: {student.student_id}, Class: {student.grade_level})")

        print("\nStudent-Subject Enrollments:")
        for subject in subjects[:10]:  # Show first 10
            student_name = subject.student.user.full_name if subject.student and subject.student.user else f"Student {subject.student_id}"
            print(f"  - {student_name}: {subject.subject} ({subject.status})")

        if len(subjects) > 10:
            print(f"  ... and {len(subjects) - 10} more")

if __name__ == "__main__":
    check_database()
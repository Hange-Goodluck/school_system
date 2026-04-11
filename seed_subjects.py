#!/usr/bin/env python3
"""
Data seeding script for the School Management System.
This script populates students with the 15 core Nigerian subjects.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, select
from backend.db.database import engine
from backend.models import Student, StudentSubject

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
    "Trade/Vocational Studies",
    "Physical Education",
    "Music",
    "Visual Arts"
]

def seed_student_subjects():
    """Seed all students with the 15 core Nigerian subjects."""
    print("🌱 Starting student-subject seeding process...")

    with Session(engine) as session:
        # Get all students
        students = session.exec(select(Student)).all()

        if not students:
            print("❌ No students found in the database. Please create some students first.")
            return

        print(f"📚 Found {len(students)} students to seed with subjects")

        total_enrollments_created = 0

        for student in students:
            student_name = student.user.full_name if student.user else f"Student {student.id}"
            print(f"📝 Processing {student_name} (Class: {student.grade_level})")

            # Check existing enrollments for this student
            existing_subjects = session.exec(
                select(StudentSubject).where(StudentSubject.student_id == student.id)
            ).all()

            existing_subject_names = {es.subject for es in existing_subjects}

            # Add missing subjects
            subjects_added = 0
            for subject in NIGERIAN_SUBJECTS:
                if subject not in existing_subject_names:
                    enrollment = StudentSubject(
                        student_id=student.id,
                        subject=subject,
                        status="enrolled"
                    )
                    session.add(enrollment)
                    subjects_added += 1
                    total_enrollments_created += 1

            if subjects_added > 0:
                print(f"   ✅ Added {subjects_added} new subjects")
            else:
                print(f"   ℹ️  Already has all subjects")

        # Commit all changes
        session.commit()

        print("\n🎉 Seeding completed successfully!")
        print(f"📊 Total enrollments created: {total_enrollments_created}")
        print(f"📚 Total subjects per student: {len(NIGERIAN_SUBJECTS)}")
        print(f"👥 Total students processed: {len(students)}")

def verify_seeding():
    """Verify that seeding was successful."""
    print("\n🔍 Verifying seeding results...")

    with Session(engine) as session:
        # Count total enrollments
        total_enrollments = session.exec(select(StudentSubject)).all()
        print(f"📊 Total student-subject enrollments: {len(total_enrollments)}")

        # Check distribution by class
        students = session.exec(select(Student)).all()
        class_distribution = {}

        for student in students:
            grade_level = student.grade_level or "Unknown"
            if grade_level not in class_distribution:
                class_distribution[grade_level] = 0

            # Count subjects for this student
            subject_count = len(session.exec(
                select(StudentSubject).where(StudentSubject.student_id == student.id)
            ).all())

            class_distribution[grade_level] += subject_count

        print("📈 Subject distribution by class:")
        for class_name, total_subjects in sorted(class_distribution.items()):
            student_count = len([s for s in students if (s.grade_level or "Unknown") == class_name])
            avg_subjects = total_subjects / student_count if student_count > 0 else 0
            print(f"   {class_name}: {student_count} students, {total_subjects} total subjects (avg: {avg_subjects:.1f} per student)")

if __name__ == "__main__":
    print("🏫 School Management System - Student Subject Seeding")
    print("=" * 60)

    try:
        seed_student_subjects()
        verify_seeding()

        print("\n✅ All done! You can now view the student register at /student-register")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        sys.exit(1)
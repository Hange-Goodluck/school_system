#!/usr/bin/env python3
"""
Manually create the student_subjects table since alembic is not working
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlmodel import SQLModel
from backend.db.database import engine
from backend.models import StudentSubject

def create_tables():
    """Create all tables that don't exist"""
    print("Creating student_subjects table...")

    # Create the table
    SQLModel.metadata.create_all(engine, tables=[StudentSubject.__table__])

    print("✅ Table created successfully!")

if __name__ == "__main__":
    create_tables()
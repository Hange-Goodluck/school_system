from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
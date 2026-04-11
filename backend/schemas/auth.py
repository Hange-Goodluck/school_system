from pydantic import BaseModel, Field, EmailStr
from backend.models.enums import UserRole

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
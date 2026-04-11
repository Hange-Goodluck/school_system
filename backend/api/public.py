from fastapi import Depends, HTTPException, APIRouter, status
from sqlmodel import Session
from backend.db.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.auth import UserResponse


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )
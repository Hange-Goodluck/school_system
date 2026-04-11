from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.db.database import get_db
from backend.models.user import User
from backend.schemas.auth import UserCreate, UserLogin, TokenResponse
from backend.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(user_data: UserCreate, session: Session = Depends(get_db)):
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

    token = create_access_token({"sub": str(user.id), "role": user.role})

    return {"access_token": token}


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, session: Session = Depends(get_db)):
    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})

    return {"access_token": token, "token_type": "bearer"}



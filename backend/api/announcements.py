from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from backend.db.database import get_db
from backend.models import Announcement, User
from backend.models.enums import UserRole
from backend.schemas.announcement import AnnouncementCreate, AnnouncementResponse
from backend.core.dependencies import get_current_user

router = APIRouter(prefix="/announcements", tags=["Announcements"])

@router.post("/", response_model=AnnouncementResponse)
def create_announcement(
    announcement_data: AnnouncementCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Only teachers and admins can create announcements
    if current_user.role not in [UserRole.teacher, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Not authorized to create announcements")

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

@router.get("/", response_model=List[AnnouncementResponse])
def list_announcements(
    session: Session = Depends(get_db)
):
    announcements = session.exec(
        select(Announcement).where(Announcement.is_published == True)
    ).all()
    return announcements

@router.get("/{announcement_id}", response_model=AnnouncementResponse)
def get_announcement(
    announcement_id: int,
    session: Session = Depends(get_db)
):
    announcement = session.get(Announcement, announcement_id)
    if not announcement or not announcement.is_published:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement
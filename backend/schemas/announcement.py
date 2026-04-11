from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    is_published: bool = True

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None

class AnnouncementResponse(BaseModel):
    id: int
    title: str
    content: str
    is_published: bool
    published_at: Optional[datetime]
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime]
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from backend.models.base import TimestampMixin

if TYPE_CHECKING:
    from backend.models.user import User


class Admin(TimestampMixin, SQLModel, table=True):
    __tablename__ = "admins"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    admin_level: str = Field(default="standard")  # e.g., "super", "standard"

    # Relationship to the base user account
    user: Optional["User"] = Relationship(back_populates="admin_profile")

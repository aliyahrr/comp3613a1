import datetime as dt
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.user import User


class HoursStatus(str, Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"


class VolunteerHours(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    student_id: int = Field(foreign_key="user.id", index=True)
    activity: str
    date: dt.date
    hours: float
    proof: str
    date_submitted: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc)
    )

    status: HoursStatus = Field(default=HoursStatus.Pending, index=True)
    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    comment: Optional[str] = None
    date_reviewed: Optional[dt.datetime] = None

    student: Optional["User"] = Relationship(
            back_populates="submitted_hours",
            sa_relationship_kwargs={"foreign_keys": "[VolunteerHours.student_id]"},
        )

    reviewer: Optional["User"] = Relationship(
        back_populates="reviewed_hours",
        sa_relationship_kwargs={"foreign_keys": "[VolunteerHours.reviewed_by]"},
    )

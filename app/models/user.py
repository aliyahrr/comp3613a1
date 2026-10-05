from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List, TYPE_CHECKING
from pydantic import EmailStr

if TYPE_CHECKING:
    from app.models.volunteer_hours import VolunteerHours


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role: str = ""


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    approved_hours: float = Field(default=0.0)
    lifetime_hours: float = Field(default=0.0)

    submitted_hours: List["VolunteerHours"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"foreign_keys": "[VolunteerHours.student_id]"},
    )

    reviewed_hours: List["VolunteerHours"] = Relationship(
        back_populates="reviewer",
        sa_relationship_kwargs={"foreign_keys": "[VolunteerHours.reviewed_by]"},
    )

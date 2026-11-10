from datetime import date, datetime

from sqlmodel import SQLModel

from app.models.volunteer_hours import HoursStatus


class VolunteerHoursRead(SQLModel):
    id: int
    student_id: int
    activity: str
    date: date
    hours: float
    status: HoursStatus
    comment: str | None = None
    date_submitted: datetime

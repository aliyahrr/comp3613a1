from sqlmodel import Session, select

from app.models.user import User
from app.models.volunteer_hours import HoursStatus, VolunteerHours


class VolunteerHoursRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_submission(self, submission: VolunteerHours) -> VolunteerHours:
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def get_for_student(self, student_id: int) -> list[VolunteerHours]:
        statement = (
            select(VolunteerHours)
            .where(VolunteerHours.student_id == student_id)
            .order_by(VolunteerHours.date_submitted.desc())
        )
        return self.db.exec(statement).all()

    def get_pending_submissions(self) -> list[VolunteerHours]:
        statement = (
            select(VolunteerHours)
            .where(VolunteerHours.status == HoursStatus.Pending)
            .order_by(VolunteerHours.date_submitted.asc())
        )
        return self.db.exec(statement).all()

    def get_by_id(self, submission_id: int) -> VolunteerHours | None:
        return self.db.get(VolunteerHours, submission_id)

    def save_review(self, submission: VolunteerHours, student: User) -> VolunteerHours:
        self.db.add(submission)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(submission)
        return submission
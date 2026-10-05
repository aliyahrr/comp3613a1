import shutil
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import UploadFile

from app.models.volunteer_hours import HoursStatus, VolunteerHours
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.repositories.user import UserRepository

upload_dir = Path("uploads")
allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}


class VolunteerHoursService:
    def __init__(
        self,
        repository: VolunteerHoursRepository,
        user_repository: UserRepository,
    ):
        self.repository = repository
        self.user_repository = user_repository

    def submit_hours(
        self,
        *,
        student_id: int,
        activity: str,
        date_completed: date,
        hours: float,
        proof_file: UploadFile,
    ) -> VolunteerHours:
        if hours <= 0:
            raise ValueError("Hours must be more than zero.")

        extension = Path(proof_file.filename or "").suffix.lower()
        if extension not in allowed_extensions:
            raise ValueError("Invalid file type for proof, must be PDF, PNG, JPG, or JPEG.")

        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4().hex}{extension}"
        file_path = upload_dir / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(proof_file.file, buffer)

        submission = VolunteerHours(
            student_id=student_id,
            activity=activity,
            date=date_completed,
            hours=hours,
            proof=file_path.as_posix(),
            status=HoursStatus.Pending,
        )

        try:
            return self.repository.create_submission(submission)
        except Exception:
            file_path.unlink(missing_ok=True)
            raise

    def get_student_submissions(self, student_id: int) -> list[VolunteerHours]:
        return self.repository.get_for_student(student_id)

    def get_pending_submissions(self) -> list[VolunteerHours]:
        return self.repository.get_pending_submissions()

    def get_submission(self, submission_id: int) -> VolunteerHours | None:
        return self.repository.get_by_id(submission_id)

    def review_submission(
        self,
        *,
        submission_id: int,
        reviewer_id: int,
        approved: bool,
        comment: str | None,
    ) -> VolunteerHours:
        submission_id = int(submission_id)
        submission = self.repository.get_by_id(submission_id)
        if not submission:
            raise ValueError("Submission not found.")

        
        if submission.status != HoursStatus.Pending:
            raise ValueError("Only pending submissions can be reviewed.")

        clean_comment = comment.strip() if comment else ""

        
        if not approved and not clean_comment:
            raise ValueError("A comment is required when rejecting a submission.")

        student = self.user_repository.get_by_id(submission.student_id)
        if not student:
            raise ValueError("Student not found.")

        submission.comment = clean_comment or None
        submission.reviewed_by = reviewer_id
        submission.date_reviewed = datetime.now(timezone.utc)
        submission.status = HoursStatus.Approved if approved else HoursStatus.Rejected

        if approved:
            student.approved_hours += submission.hours
            student.lifetime_hours += submission.hours

        return self.repository.save_review(submission, student)
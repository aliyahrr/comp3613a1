from __future__ import annotations

from datetime import date
from io import BytesIO

import pytest
from fastapi import UploadFile

from app.models.prize import Prize
from app.models.user import User
from app.models.volunteer_hours import HoursStatus, VolunteerHours
from app.repositories.prize import PrizeRepository
from app.repositories.user import UserRepository
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.services.prize_service import PrizeService
from app.services.volunteer_hours_service import VolunteerHoursService
from app.utilities.security import encrypt_password


@pytest.fixture()
def student(test_session):
    user = User(
        username="student1",
        email="student1@example.com",
        password=encrypt_password("pass123"),
        role="regular_user",
        approved_hours=0.0,
        lifetime_hours=0.0,
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture()
def admin(test_session):
    user = User(
        username="admin1",
        email="admin1@example.com",
        password=encrypt_password("pass123"),
        role="admin",
        approved_hours=0.0,
        lifetime_hours=0.0,
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


def test_submit_hours_rejects_invalid_hours(test_session, student):
    service = VolunteerHoursService(VolunteerHoursRepository(test_session), UserRepository(test_session))

    with pytest.raises(ValueError, match="Hours must be more than zero"):
        service.submit_hours(
            student_id=student.id,
            activity="Library Help",
            date_completed=date(2025, 1, 2),
            hours=0,
            proof_file=UploadFile(filename="proof.png", file=BytesIO(b"pngdata")),
        )


def test_review_submission_approves_hours_and_updates_totals(test_session, student, admin):
    service = VolunteerHoursService(VolunteerHoursRepository(test_session), UserRepository(test_session))
    submission = service.submit_hours(
        student_id=student.id,
        activity="Mentoring",
        date_completed=date(2025, 1, 2),
        hours=3.5,
        proof_file=UploadFile(filename="proof.png", file=BytesIO(b"pngdata")),
    )

    approved = service.review_submission(
        submission_id=submission.id,
        reviewer_id=admin.id,
        approved=True,
        comment="Looks good",
    )

    assert approved.status == HoursStatus.Approved
    refreshed_student = test_session.get(User, student.id)
    assert refreshed_student.approved_hours == 3.5
    assert refreshed_student.lifetime_hours == 3.5


def test_redeem_prize_updates_stock_and_balance(test_session, student):
    prize = Prize(name="T-shirt", description="Branded tee", cost=4, stock=2)
    test_session.add(prize)
    test_session.commit()
    test_session.refresh(prize)

    student.approved_hours = 10.0
    test_session.add(student)
    test_session.commit()

    service = PrizeService(PrizeRepository(test_session))
    redemption = service.redeem_prize(student.id, prize.id)

    refreshed_student = test_session.get(User, student.id)
    refreshed_prize = test_session.get(Prize, prize.id)

    assert refreshed_student.approved_hours == 6.0
    assert refreshed_prize.stock == 1
    assert redemption.hours_spent == 4

from __future__ import annotations

from datetime import date

from sqlmodel import Session

from app.models.prize import Prize
from app.models.user import User
from app.models.volunteer_hours import HoursStatus, VolunteerHours
from app.repositories.prize import PrizeRepository
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.utilities.security import create_access_token, encrypt_password


def _login(client, user):
    token = create_access_token({"sub": str(user.id), "role": user.role})
    client.cookies.set("access_token", token)


def test_student_can_submit_hours(client, engine, test_session):
    user = User(
        username="student2",
        email="student2@example.com",
        password=encrypt_password("pass123"),
        role="regular_user",
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    _login(client, user)
    response = client.post(
        "/app/hours/submit",
        data={
            "activity": "Campus tour guide",
            "date_completed": "2025-02-03",
            "hours": "2.5",
        },
        files={"proof_file": ("proof.png", b"fakepng", "image/png")},
        follow_redirects=False,
    )

    assert response.status_code == 303
    with Session(engine) as fresh_session:
        submissions = VolunteerHoursRepository(fresh_session).get_for_student(user.id)
        assert len(submissions) == 1
        assert submissions[0].status == HoursStatus.Pending


def test_zero_hours_request_fails_form_validation(client, test_session):
    student = User(
        username="student_zero",
        email="student_zero@example.com",
        password=encrypt_password("pass123"),
        role="regular_user",
    )
    test_session.add(student)
    test_session.commit()
    test_session.refresh(student)

    _login(client, student)
    response = client.post(
        "/app/hours/submit",
        data={
            "activity": "Invalid zero-hour submission",
            "date_completed": "2025-02-05",
            "hours": "0",
        },
        files={"proof_file": ("proof.pdf", b"%PDF-1.1", "application/pdf")},
        follow_redirects=False,
    )

    assert response.status_code == 422


def test_admin_can_review_a_pending_submission(client, engine, test_session):
    student = User(
        username="student3",
        email="student3@example.com",
        password=encrypt_password("pass123"),
        role="regular_user",
    )
    admin = User(
        username="admin2",
        email="admin2@example.com",
        password=encrypt_password("pass123"),
        role="admin",
    )
    test_session.add_all([student, admin])
    test_session.commit()
    test_session.refresh(student)
    test_session.refresh(admin)

    submission = VolunteerHours(
        student_id=student.id,
        activity="Orientation support",
        date=date(2025, 2, 4),
        hours=4.0,
        proof="uploads/proof.png",
        status=HoursStatus.Pending,
    )
    test_session.add(submission)
    test_session.commit()
    test_session.refresh(submission)

    _login(client, admin)
    response = client.post(
        f"/admin/hours/{submission.id}/review",
        data={"decision": "approve", "comment": "Approved"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    with Session(engine) as fresh_session:
        updated = VolunteerHoursRepository(fresh_session).get_by_id(submission.id)
        assert updated.status == HoursStatus.Approved
        assert fresh_session.get(User, student.id).approved_hours == 4.0


def test_student_can_redeem_reward(client, engine, test_session):
    student = User(
        username="student4",
        email="student4@example.com",
        password=encrypt_password("pass123"),
        role="regular_user",
        approved_hours=10.0,
    )
    prize = Prize(name="Waterbottle", description="Reusable bottle", cost=3, stock=2)
    test_session.add_all([student, prize])
    test_session.commit()
    test_session.refresh(student)
    test_session.refresh(prize)

    _login(client, student)
    response = client.post(
        f"/app/prizes/{prize.id}/redeem",
        follow_redirects=False,
    )

    assert response.status_code == 303
    with Session(engine) as fresh_session:
        assert PrizeRepository(fresh_session).get_by_id(prize.id).stock == 1


def test_unauthenticated_admin_request_returns_401(client):
    response = client.get("/admin")

    assert response.status_code == 401


def test_student_admin_request_returns_403(client, test_session):
    student = User(
        username="student5",
        email="student5@example.com",
        password=encrypt_password("pass123"),
        role="regular_user",
    )
    test_session.add(student)
    test_session.commit()
    test_session.refresh(student)

    _login(client, student)
    response = client.get("/admin")

    assert response.status_code == 403

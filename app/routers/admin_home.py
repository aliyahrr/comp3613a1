from pathlib import Path

from fastapi import Form, HTTPException, Request, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app.dependencies.auth import AdminDep
from app.dependencies.session import SessionDep
from app.models.volunteer_hours import HoursStatus
from app.repositories.user import UserRepository
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.services.volunteer_hours_service import VolunteerHoursService

from . import router, templates


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    service = VolunteerHoursService(
        VolunteerHoursRepository(db),
        UserRepository(db),
    )
    pending_submissions = service.get_pending_submissions()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": user,
            "pending_submissions": pending_submissions,
        },
    )


@router.get("/admin/hours/{submission_id}/proof", name="admin_view_proof")
def admin_view_proof(
    submission_id: int,
    user: AdminDep,
    db: SessionDep,
):
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be signed in to view proof files.",
        )

    service = VolunteerHoursService(
        VolunteerHoursRepository(db),
        UserRepository(db),
    )
    submission = service.get_submission(submission_id)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found.",
        )

    upload_root = Path("uploads").resolve()
    proof_path = Path(submission.proof)
    if not proof_path.is_absolute():
        proof_path = Path.cwd() / proof_path
    proof_path = proof_path.resolve()

    try:
        proof_path.relative_to(upload_root)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proof file not found.",
        ) from error

    if not proof_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proof file not found.",
        )

    return FileResponse(path=proof_path, filename=proof_path.name)


@router.get("/admin/hours/{submission_id}", name="admin_review_view")
def admin_review_view(
    request: Request,
    submission_id: int,
    user: AdminDep,
    db: SessionDep,
):
    service = VolunteerHoursService(
        VolunteerHoursRepository(db),
        UserRepository(db),
    )
    submission = service.get_submission(submission_id)
    if submission is None or submission.status != HoursStatus.Pending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending submission not found.",
        )

    return templates.TemplateResponse(
        request=request,
        name="review_hours.html",
        context={"user": user, "submission": submission},
    )


@router.post("/admin/hours/{submission_id}/review", name="review_volunteer_hours")
def review_volunteer_hours(
    request: Request,
    submission_id: int,
    user: AdminDep,
    db: SessionDep,
    decision: str = Form(),
    comment: str | None = Form(default=None),
):
    decision_value = decision.strip().lower()
    if decision_value not in ("approve", "reject"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision must be either 'approve' or 'reject'.",
        )

    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be signed in to review hours.",
        )

    service = VolunteerHoursService(
        VolunteerHoursRepository(db),
        UserRepository(db),
    )

    try:
        service.review_submission(
            submission_id=submission_id,
            reviewer_id=user.id,
            approved=(decision_value == "approve"),
            comment=comment,
        )
    except ValueError as error:
        submission = service.get_submission(submission_id)
        if submission is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pending submission not found.",
            ) from error
        return templates.TemplateResponse(
            request=request,
            name="review_hours.html",
            context={"user": user, "submission": submission, "error": str(error)},
        )

    return RedirectResponse(
        url=request.url_for("admin_home_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
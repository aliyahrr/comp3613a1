from fastapi import Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep
from app.models.volunteer_hours import HoursStatus
from app.repositories.user import UserRepository
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.services.volunteer_hours_service import VolunteerHoursService
from . import router, templates


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db:SessionDep
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
        }
    )


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pending submission not found.")

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
    # STUDENT TODO: bind the review to the service and redirect to Approvals.
    raise NotImplementedError("Complete the review_volunteer_hours route")

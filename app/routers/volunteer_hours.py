from datetime import date

from fastapi import File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.repositories.user import UserRepository
from app.services.volunteer_hours_service import VolunteerHoursService
from . import router, templates


@router.get("/app/hours/new", name="submit_volunteer_hours_form")
def submit_volunteer_hours_form(request: Request, user: AuthDep):
    return templates.TemplateResponse(
        request=request,
        name="submit_hours.html",
        context={"user": user},
    )


@router.post("/app/hours/submit", name="submit_volunteer_hours")
def submit_volunteer_hours(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    activity: str = Form(),
    date_completed: date = Form(),
    hours: float = Form(),
    proof_file: UploadFile = File(),
):
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be signed in to submit hours.",
        )

    service = VolunteerHoursService(
        VolunteerHoursRepository(db=db),
        UserRepository(db),
    )

    try:
        service.submit_hours(
            student_id=user.id,
            activity=activity,
            date_completed=date_completed,
            hours=hours,
            proof_file=proof_file,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except OSError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the proof file. Please try again.",
        )

    return RedirectResponse(
        url=request.url_for("user_home_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
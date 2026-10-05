from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.repositories.user import UserRepository
from app.services.volunteer_hours_service import VolunteerHoursService
from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db:SessionDep
):
    if user.id is None:
        raise HTTPException(status_code=500, detail="The signed-in user has no database id.")

    service = VolunteerHoursService(
        VolunteerHoursRepository(db),
        UserRepository(db),
    )
    submissions = service.get_student_submissions(user.id)

    return templates.TemplateResponse(
        request=request, 
        name="app.html",
        context={
            "user": user,
            "submissions": submissions,
        }
    )
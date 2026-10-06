from io import BytesIO

import qrcode
from fastapi import HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.models.user import User
from app.repositories.prize import PrizeRepository
from app.services.prize_service import PrizeService
from app.utilities.flash import flash

from . import router, templates


def _service(db: SessionDep) -> PrizeService:
    return PrizeService(PrizeRepository(db))


def _student_id(user: User) -> int:
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be signed in to access prizes.",
        )
    return user.id


@router.get("/app/prizes", response_class=HTMLResponse, name="prizes_view")
def prizes_view(request: Request, user: AuthDep, db: SessionDep):
    service = _service(db)
    return templates.TemplateResponse(
        request=request,
        name="prizes.html",
        context={
            "user": user,
            "prizes": service.list_prizes(),
        },
    )


@router.get(
    "/app/prizes/{prize_id}/confirm",
    response_class=HTMLResponse,
    name="prize_confirm_view",
)
def prize_confirm_view(
    request: Request,
    prize_id: int,
    user: AuthDep,
    db: SessionDep,
):
    prize = _service(db).get_prize(prize_id)
    if prize is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prize not found.")

    if prize.stock <= 0:
        flash(request, "That prize is out of stock. Check back soon!", type="warning")
        return RedirectResponse(
            url=request.url_for("prizes_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    shortfall = prize.cost - user.approved_hours
    if shortfall > 0:
        return templates.TemplateResponse(
            request=request,
            name="prize_shortfall.html",
            context={"user": user, "prize": prize, "shortfall": shortfall},
        )

    return templates.TemplateResponse(
        request=request,
        name="prize_confirm.html",
        context={
            "user": user,
            "prize": prize,
            "balance_after": user.approved_hours - prize.cost,
        },
    )


@router.post("/app/prizes/{prize_id}/redeem", name="redeem_prize")
def redeem_prize(
    request: Request,
    prize_id: int,
    user: AuthDep,
    db: SessionDep,
):
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be signed in to redeem a prize.",
        )

    service = PrizeService(PrizeRepository(db))
    try:
        redemption = service.redeem_prize(user.id, prize_id)
    except ValueError as error:
        flash(request, str(error), type="danger")
        return RedirectResponse(
            url=request.url_for("prizes_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return RedirectResponse(
        url=request.url_for("redemption_receipt_view", receipt_code=redemption.receipt_code),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/app/redemptions/{receipt_code}",
    response_class=HTMLResponse,
    name="redemption_receipt_view",
)
def redemption_receipt_view(
    request: Request,
    receipt_code: str,
    user: AuthDep,
    db: SessionDep,
):
    service = _service(db)
    redemption = service.get_receipt(_student_id(user), receipt_code)
    if redemption is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found.")
    prize = service.get_prize(redemption.prize_id)
    if prize is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prize not found.")
    return templates.TemplateResponse(
        request=request,
        name="redemption_receipt.html",
        context={"user": user, "redemption": redemption, "prize": prize},
    )


@router.get("/app/redemptions/{receipt_code}/qr", name="redemption_qr")
def redemption_qr(
    receipt_code: str,
    user: AuthDep,
    db: SessionDep,
):
    redemption = _service(db).get_receipt(_student_id(user), receipt_code)
    if redemption is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found.")

    image = qrcode.make(redemption.receipt_code)
    image_bytes = BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    return StreamingResponse(image_bytes, media_type="image/png")

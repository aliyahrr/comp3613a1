from sqlmodel import Session, select

from app.models.prize import Prize
from app.models.redemption import Redemption
from app.models.user import User


class PrizeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_prizes(self) -> list[Prize]:
        statement = select(Prize).order_by(Prize.cost.desc())
        return self.db.exec(statement).all()

    def get_by_id(self, prize_id: int) -> Prize | None:
        return self.db.get(Prize, prize_id)

    def get_by_name(self, name: str) -> Prize | None:
        statement = select(Prize).where(Prize.name == name)
        return self.db.exec(statement).one_or_none()

    def create_prize(self, prize: Prize) -> Prize:
        self.db.add(prize)
        self.db.commit()
        self.db.refresh(prize)
        return prize

    def lock_for_redemption(
        self,
        student_id: int,
        prize_id: int,
    ) -> tuple[User | None, Prize | None]:
        user_statement = (
            select(User).where(User.id == student_id).with_for_update()
        )
        prize_statement = (
            select(Prize).where(Prize.id == prize_id).with_for_update()
        )
        user = self.db.exec(user_statement).one_or_none()
        prize = self.db.exec(prize_statement).one_or_none()
        return user, prize

    def save_redemption(
        self,
        redemption: Redemption,
        user: User,
        prize: Prize,
    ) -> Redemption:
        self.db.add(user)
        self.db.add(prize)
        self.db.add(redemption)
        self.db.commit()
        self.db.refresh(redemption)
        return redemption

    def get_redemption_by_code(self, receipt_code: str) -> Redemption | None:
        statement = select(Redemption).where(Redemption.receipt_code == receipt_code)
        return self.db.exec(statement).one_or_none()

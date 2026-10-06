from app.models.prize import Prize
from app.models.redemption import Redemption
from app.repositories.prize import PrizeRepository


class PrizeService:
    def __init__(self, repository: PrizeRepository):
        self.repository = repository

    def list_prizes(self) -> list[Prize]:
        return self.repository.list_prizes()

    def get_prize(self, prize_id: int) -> Prize | None:
        return self.repository.get_by_id(prize_id)

    def redeem_prize(self, student_id: int, prize_id: int) -> Redemption:
        student, prize = self.repository.lock_for_redemption(student_id, prize_id)

        if student is None:
            raise ValueError("Student not found.")
        if prize is None:
            raise ValueError("Prize not found.")
        if prize.stock <= 0:
            raise ValueError("Prize is out of stock.")
        if student.approved_hours < prize.cost:
            shortfall = prize.cost - student.approved_hours
            raise ValueError(
                f"Not enough approved hours. You need {shortfall} more hours to redeem this prize."
            )
        if student.id is None or prize.id is None:
            raise ValueError("Student or prize record is not saved.")

        student.approved_hours -= prize.cost
        prize.stock -= 1

        redemption = Redemption(
            student_id=student.id,
            prize_id=prize.id,
            hours_spent=prize.cost,
        )

        return self.repository.save_redemption(redemption, student, prize)

    def get_receipt(self, student_id: int, receipt_code: str) -> Redemption | None:
        redemption = self.repository.get_redemption_by_code(receipt_code)
        if redemption is None or redemption.student_id != student_id:
            return None
        return redemption
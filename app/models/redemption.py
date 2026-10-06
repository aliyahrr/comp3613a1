import secrets
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Redemption(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    prize_id: int = Field(foreign_key="prize.id", index=True)
    hours_spent: float
    redeemed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    receipt_code: str = Field(default_factory=lambda: secrets.token_hex(8).upper(),unique=True, index=True
                              
    )
    

    

from datetime import datetime as dt
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt


class DonationBase(BaseModel):
    user_id: Optional[int]
    comment: Optional[str]
    full_amount: PositiveInt
    invested_amount: int = Field(default=0)
    fully_invested: bool = Field(default=False)
    create_date: Optional[dt] = Field(default_factory=dt.now)
    close_date: Optional[dt]

    class Config:
        extra = Extra.forbid


class DonationCreate(DonationBase):
    pass


class DonationDB(DonationBase):
    id: int

    class Config:
        orm_mode = True

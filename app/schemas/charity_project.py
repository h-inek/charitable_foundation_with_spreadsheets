from datetime import datetime as dt
from typing import Optional

from pydantic import (
    BaseModel, Extra, Field, PositiveInt
)

from app.constants import (
    DEFAULT_INVESTED_AMOUNT, MIN_VALUE_STR_FIELD, MAX_VALUE_STR_FIELD
)


class CharityProjectBase(BaseModel):
    full_amount: PositiveInt
    invested_amount: int = Field(DEFAULT_INVESTED_AMOUNT)
    fully_invested: bool = Field(False)
    create_date: dt = Field(example=dt.now)
    close_date: Optional[dt] = Field(None, example=dt.now)


class CharityProjectCreate(BaseModel):
    name: str = Field(
        min_length=MIN_VALUE_STR_FIELD,
        max_length=MAX_VALUE_STR_FIELD
    )
    description: str = Field(min_length=MIN_VALUE_STR_FIELD)
    full_amount: PositiveInt = Field()


class CharityProjectUpdate(CharityProjectCreate):
    name: str = Field(
        None,
        min_length=MIN_VALUE_STR_FIELD,
        max_length=MAX_VALUE_STR_FIELD
    )
    description: str = Field(None, min_length=MIN_VALUE_STR_FIELD)
    full_amount: PositiveInt = Field(None)

    class Config:
        extra = Extra.forbid


class CharityProjectDB(CharityProjectCreate, CharityProjectBase):
    id: int

    class Config:
        orm_mode = True

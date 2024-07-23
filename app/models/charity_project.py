from sqlalchemy import Column, String, Text

from app.core.db import AbstractModel


class CharityProject(AbstractModel):
    name = Column(String)
    description = Column(Text)

    def __repr__(self):
        return (
            f'Проект {self.name} рассчитывает на сумму {self.full_amount}'
        )

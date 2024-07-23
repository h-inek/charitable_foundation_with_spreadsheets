from sqlalchemy import Column, ForeignKey, Integer, Text

from app.core.db import AbstractModel


class Donation(AbstractModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)

    def __repr__(self):
        return (
            f'Донат от {self.user_id} на сумму {self.full_amount}'
        )

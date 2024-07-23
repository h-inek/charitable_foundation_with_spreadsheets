from datetime import datetime as dt
from typing import Union

from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.base import CRUDBase
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.charity_project import CharityProject
from app.models.donation import Donation


class CharityProjectService:

    def __init__(self, session: AsyncSession):
        self.session = session

    def _close_item(self, item):
        """Вспомогательная функция для закрытия объекта(проект/донат)."""
        item.fully_invested = True
        item.close_date = dt.now()

    def _check_not_null_invested_amount(
            self,
            charity_project,
    ) -> CharityProject:
        """Проверяем на внесение средств в проект."""
        if charity_project.invested_amount > 0:
            raise HTTPException(
                status_code=400,
                detail='В проект внесения средства!'
            )

        return charity_project

    async def _check_name_duplicate(self, project_name):
        """Проверка на повторяющееся имя."""
        project_id = await charity_project_crud.get_project_id_by_name(
            project_name, self.session
        )
        if project_id is not None:
            raise HTTPException(
                status_code=400,
                detail='Проект с таким именем уже существует!',
            )

    def _check_update_close_project(
            self,
            project: CharityProject,
    ) -> None:
        """Проверка проекта на закрытие."""
        if project.fully_invested:
            raise HTTPException(
                status_code=400,
                detail='Нельзя редактировать закрытый проект!'
            )

    async def invest_with_create(
            self,
            item: Union[Donation, CharityProject],
            session: AsyncSession = Depends(get_async_session)
    ):
        """Процесс инвестирования"""
        unallocated = await CRUDBase(
            Donation if isinstance(item, CharityProject) else CharityProject
        ).get_partial(session)

        if unallocated:
            for obj in unallocated:
                residual_amount = obj.full_amount - obj.invested_amount
                if residual_amount == item.full_amount:
                    self._close_item(item)
                    item.invested_amount += item.full_amount
                    self._close_item(obj)
                    obj.invested_amount += item.full_amount

                    break

                if residual_amount < item.full_amount:
                    item.invested_amount += residual_amount
                    self._close_item(obj)
                    obj.invested_amount += residual_amount
                if residual_amount > item.full_amount:
                    self._close_item(item)
                    item.invested_amount += item.full_amount
                    obj.invested_amount += item.full_amount

                    break

                session.add(obj)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item

    async def check_amount_and_update_project(
            self,
            obj_data,
            different
    ) -> CharityProject:
        if different > 0:
            raise HTTPException(
                status_code=400,
                detail='Сумма пожертований не может быть меньше изначальной!'
            )
        if different == 0:
            self._close_item(obj_data)
            self.session.add(obj_data)
            await self.session.commit()
            await self.session.refresh(obj_data)

        return obj_data

    async def create_project(
            self,
            new_project
    ):
        await self._check_name_duplicate(new_project.name)
        new_project = await charity_project_crud.create(
            new_project, self.session
        )
        new_project = await self.invest_with_create(new_project, self.session)
        return new_project

    async def update_project(
            self,
            project,
            update_data
    ):

        self._check_update_close_project(project)

        if update_data.name != project.name:
            await self._check_name_duplicate(update_data.name)

        if update_data.full_amount is not None:
            await self.check_amount_and_update_project(
                project,
                different=project.invested_amount - update_data.full_amount
            )

        project = await charity_project_crud.update(
            project, update_data, self.session
        )

        return project

    async def delete_project(
            self,
            project
    ):
        project = self._check_not_null_invested_amount(project)
        project = await charity_project_crud.remove(
            project, self.session
        )

        return project

    async def create_donation(
            self,
            new_donation,
            user
    ):
        new_donation = await donation_crud.create(
            new_donation, self.session, user
        )
        new_donation = await self.invest_with_create(
            new_donation, self.session
        )
        return new_donation

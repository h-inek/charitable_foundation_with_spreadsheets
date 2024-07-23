from datetime import datetime as dt

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models.charity_project import CharityProject


async def get_project_or_404(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    """Поиск проекта по id. Возвращаем либо проект. либо ошибку 404"""
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден!'
        )
    return charity_project


def format_time(time):
    """Вспомогательная функция для перевода времени из строки в datetime"""
    return dt.strptime(time, '%Y-%m-%d %H:%M:%S')

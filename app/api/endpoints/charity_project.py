from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectDB, CharityProjectCreate, CharityProjectUpdate
)
from app.services.charity_project_service import CharityProjectService
from app.utils import get_project_or_404

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session)
):

    return await CharityProjectService(session).create_project(
        charity_project
    )


@router.get(
    '/{charity_project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_charity_project(
        charity_project_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    new_project = await get_project_or_404(charity_project_id, session)
    return new_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_project(
        session: AsyncSession = Depends(get_async_session)
):
    new_project = await charity_project_crud.get_multi(session)
    return new_project


@router.delete(
    '/{charity_project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_charity_project(
        charity_project_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    project = await get_project_or_404(
        charity_project_id,
        session
    )
    return await CharityProjectService(session).delete_project(
        project
    )


@router.patch(
    '/{charity_project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def partially_update_charity_project(
        charity_project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    project = await get_project_or_404(charity_project_id, session)

    return await CharityProjectService(session).update_project(
        project,
        obj_in
    )

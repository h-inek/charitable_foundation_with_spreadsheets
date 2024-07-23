from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.donation import donation_crud
from app.schemas.donation import DonationDB, DonationCreate
from app.services.charity_project_service import CharityProjectService
from app.models.user import User


router = APIRouter()


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    response_model_exclude={
        'invested_amount', 'fully_invested', 'close_date', 'user_id'
    },
    dependencies=[Depends(current_user)]
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    return await CharityProjectService(session).create_donation(
        donation,
        user
    )


@router.get(
    '/my',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    response_model_exclude={
        'invested_amount', 'fully_invested', 'close_date', 'user_id'
    },
    dependencies=[Depends(current_user)]
)
async def get_my_all_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    my_donations = await donation_crud.get_by_user(session, user)
    return my_donations


@router.get(
    '/',
    response_model=list[DonationDB],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    donations_db = await donation_crud.get_multi(session)
    return donations_db

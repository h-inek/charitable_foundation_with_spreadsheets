from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.services.google_api import GoogleApiService

router = APIRouter()


@router.post(
    '/',
    response_model=list[dict],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)
):
    google_api = GoogleApiService(session, wrapper_services)
    projects_info = await google_api.return_project_info()
    spreadsheetid = await google_api.spreadsheets_create()
    await google_api.set_user_permissions(spreadsheetid)
    await google_api.spreadsheets_update_value(
        spreadsheetid,
        projects_info
    )

    return projects_info

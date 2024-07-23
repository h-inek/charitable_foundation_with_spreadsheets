from fastapi import APIRouter

from app.api.endpoints import user_router
from app.api.endpoints import project_router
from app.api.endpoints import donation_router
from app.api.endpoints import google_router


main_router = APIRouter()
main_router.include_router(user_router)
main_router.include_router(
    project_router, prefix='/charity_project', tags=['Charity Projects']
)
main_router.include_router(
    donation_router, prefix='/donation', tags=['Donation']
)
main_router.include_router(
    google_router, prefix='/google', tags=['Google']
)

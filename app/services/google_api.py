from datetime import datetime as dt

from aiogoogle import Aiogoogle
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.charity_project_service import charity_project_crud
from app.constants import FORMAT


class GoogleApiService:

    def __init__(self, session: AsyncSession, wrapper_services: Aiogoogle):
        self.session = session
        self.wrapper_services = wrapper_services

    async def __get_projects_by_completion_rate(self):
        """Сортируем список проектов по количеству времени на сбор сбредств."""
        list_project = await charity_project_crud.get_all_charity_project(
            self.session, fully_invested=True
        )

        return sorted(
            list_project,
            key=lambda project: project.close_date - project.create_date
        )

    async def return_project_info(self):
        """Возввращаем список информации о проектах для гугл-таблицы."""
        projects = (
            await self.__get_projects_by_completion_rate()
        )
        project_info = []
        for project in projects:
            duration = project.close_date - project.create_date
            years = duration.days // 365
            months = (duration.days % 365) // 30
            days = duration.days % 30
            project_info.append(
                {
                    'project_name': project.name,
                    'duration': f'{years} year(s), '
                                f'{months} month(s), '
                                f'{days} day(s)',
                    'description': project.description
                }
            )
        return project_info

    async def spreadsheets_create(self) -> str:
        now_date_time = dt.now().strftime(FORMAT)
        service = await self.wrapper_services.discover('sheets', 'v4')
        spreadsheet_body = {
            'properties': {
                'title': f'Отчёт на {now_date_time}',
                'locale': 'ru_RU'
            },
            'sheets': [
                {
                    'properties': {
                        'sheetType': 'GRID',
                        'sheetId': 0,
                        'title': 'Лист1',
                        'gridProperties': {
                            'rowCount': 100,
                            'columnCount': 11
                        }
                    }
                }
            ]
        }
        response = await self.wrapper_services.as_service_account(
            service.spreadsheets.create(json=spreadsheet_body)
        )
        return response['spreadsheetId']

    async def set_user_permissions(
            self,
            spreadsheetid: str
    ) -> None:
        permissions_body = {'type': 'user',
                            'role': 'writer',
                            'emailAddress': settings.email}
        service = await self.wrapper_services.discover('drive', 'v3')
        await self.wrapper_services.as_service_account(
            service.permissions.create(
                fileId=spreadsheetid,
                json=permissions_body,
                fields="id"
            ))

    async def spreadsheets_update_value(
            self,
            spreadsheetid: str,
            projects_info: list[dict]
    ) -> None:
        now_date_time = dt.now().strftime(FORMAT)
        service = await self.wrapper_services.discover('sheets', 'v4')

        table_values = [
            ['Отчёт от', now_date_time],
            ['Топ проектор по скорости закрытия'],
            ['Название проекта', 'Время сбора', 'Описание']
        ]

        for project in projects_info:
            new_row = [
                str(project['project_name']),
                str(project['duration']),
                str(project['description'])
            ]
            table_values.append(new_row)

        update_body = {
            'majorDimension': 'ROWS',
            'values': table_values
        }
        await self.wrapper_services.as_service_account(
            service.spreadsheets.values.update(
                spreadsheetId=spreadsheetid,
                range='A1:E30',
                valueInputOption='USER_ENTERED',
                json=update_body
            )
        )

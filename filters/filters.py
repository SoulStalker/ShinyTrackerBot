from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_user_by_id, orm_get_tasks


# Фильтр для отлова задач на удаление из сохраненного списка пользователя
class IsUsersDelTasks(BaseFilter):
    async def __call__(self, callback: CallbackQuery, session: AsyncSession) -> bool:
        user = await orm_get_user_by_id(session, callback.from_user.id)
        tasks = await orm_get_tasks(session, user.id)
        return (callback.data[-3:] == 'del'
                and callback.data[:-3] in tasks)


# Фильтр для отлова задач на изменение из сохраненного списка пользователя
class IsUsersEditTasks(BaseFilter):
    async def __call__(self, callback: CallbackQuery, session: AsyncSession) -> bool:
        user = await orm_get_user_by_id(session, callback.from_user.id)
        tasks = await orm_get_tasks(session, user.id)
        return (callback.data[-4:] == 'edit'
                and callback.data[:-4] in tasks)


# Фильтр для отлова категорий в инлайне выбора категорий
class ShowUsersTasks(BaseFilter):
    async def __call__(self, callback: CallbackQuery, session: AsyncSession) -> bool:
        user = await orm_get_user_by_id(session, callback.from_user.id)
        tasks = await orm_get_tasks(session, user.id)
        return callback.data in tasks


# Фильтр для отлова остановки задачи
class IsStopTasks(BaseFilter):
    async def __call__(self, callback: CallbackQuery, session: AsyncSession) -> bool:
        user = await orm_get_user_by_id(session, callback.from_user.id)
        tasks = await orm_get_tasks(session, user.id)
        return (callback.data[-5:] == '_stop'
                and callback.data[:-5] in tasks)


# Фильтр для статистики по периодам
class IsInPeriods(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        periods = ('month', 'week', 'yesterday', 'today')
        return callback.data in periods

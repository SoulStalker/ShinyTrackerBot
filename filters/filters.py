from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

from database.database import users_db


# Фильтр для отлова категорий из сохраненного списка пользователя
class IsUsersCategories(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return (callback.data[-3:] == 'del'
                and callback.data[:-3] in users_db[callback.from_user.id]['categories'])

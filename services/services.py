from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Works, Task
# todo тут пусть будет работа со статистикой


# Функция возвращает статистику за день если период 0 то за сегодня если есть цифра то с этой даты
# пока сделал чтобы только за один день,
async def orm_get_day_stats(session: AsyncSession, user_id: int, period: int = 0):
    query = (select(
        Task.name,
        Works.start_time,
        Works.end_time,
    ).join(Task, Task.id == Works.task_id).order_by(Task.name).
             where(
        Works.user_id == user_id,
    ))
    # Фильтр по дате где дата больше или равно текущий год, месяц, день
    stats = await session.execute(query.filter(
        Works.start_time_year >= datetime.today().year,
        Works.start_time_month >= datetime.today().month,
        Works.start_time_day == (datetime.today().day - period)))
    for r in stats:
        print(r[0], r[1], r[2], (r[2] - r[1]).total_seconds() / 60)
    return stats


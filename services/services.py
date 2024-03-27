import asyncio

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Works, Task
from database.orm_query import orm_get_unclosed_work
from lexicon.lexicon import LEXICON_RU


# Функция возвращает статистику за день если период 0 то за сегодня если есть цифра то с этой даты
# пока сделал чтобы только за один день,
async def orm_get_day_stats(session: AsyncSession, user_id: int, period: str):
    query = (select(
        Task.name,
        Works.start_time,
        Works.end_time,
    ).join(Task, Task.id == Works.task_id).order_by(Task.name).
    where(
        Works.user_id == user_id,
        ))
    # Фильтр по дате, где дата больше или равно текущий год, месяц, день
    today = datetime.today()
    if period == 'today':
        start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)  # Начало текущего дня
        end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59)  # Конец текущего дня

        stats_query = query.filter(
            Works.start_time >= start_of_day,
            Works.end_time <= end_of_day
        )
    elif period == 'yesterday':
        yesterday = today - timedelta(days=1)

        start_of_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)  # Начало вчерашнего дня
        end_of_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)  # Конец вчерашнего дня

        stats_query = query.filter(
            Works.start_time >= start_of_yesterday,
            Works.end_time <= end_of_yesterday
        )
    elif period == 'week':
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        stats_query = query.filter(
            Works.start_time >= start_of_week,
            Works.end_time <= datetime.today()
        )
    else:
        start_of_month = datetime(today.year, today.month, 1)
        stats_query = query.filter(
            Works.start_time >= start_of_month,
            Works.end_time <= datetime.today()
        )

    stats = await session.execute(stats_query)

    return_message = ''
    result = {}
    for stat in stats:
        key = stat[0]
        time_diff = stat[2] - stat[1]
        if key in result:
            result[key] += time_diff
        else:
            result[key] = time_diff
    # Добавляем итоговое значение для всех задач
    result.setdefault(LEXICON_RU['total'], sum(result.values(), timedelta()))

    for k, v in result.items():
        print(k, v)
        return_message += f'{k}: {await get_formatted_time(v)}\n'
    return return_message


# Функция для форматирования времени
async def get_formatted_time(delta: timedelta) -> str:
    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)
    seconds = int(delta.total_seconds() % 60)

    formatted_time = f'{hours:02}:{minutes:02}:{seconds:02}'

    return formatted_time


# Тут будут храниться id сообщений бота для удаления
bot_messages_ids = {}
# todo добавить оповещение
# todo добавить очистку чата

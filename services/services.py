from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Works, Task
from lexicon.lexicon import LEXICON_RU


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
        Works.start_time_year == datetime.today().year and datetime.today().month == Works.end_time_year,
        Works.start_time_month == datetime.today().month and datetime.today().month == Works.end_time_month,
        Works.start_time_day == (datetime.today().day - period) and (datetime.today().day - period) == Works.end_time_day))

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

# todo надо добавить статистку по дням неделям и месяцу

# todo добавить оповещение

# todo добавить итоговые цифры в статистике

# todo добавить очистку чата

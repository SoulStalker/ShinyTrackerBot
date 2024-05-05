from matplotlib import pyplot as plt

from datetime import datetime, timedelta

from matplotlib.colors import TABLEAU_COLORS
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Works, Task
from lexicon.lexicon import LEXICON_RU
from database.orm_query import orm_get_tasks


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
    result = {k: v for k, v in sorted(result.items(), key=lambda item: item[1])}
    print('result: ', result)
    result.setdefault(LEXICON_RU['total'], sum(result.values(), timedelta()))
    max_name_length = max(len(k) for k in result.keys())
    for i, (k, v) in enumerate(result.items()):
        padding = " " * (max_name_length - len(k))
        return_message += f'<code>{k}{padding}: {await get_formatted_time(v)}</code>\n'
        if i == len(result) - 2:
            print("-" * (max_name_length + 1))
            return_message += f'{"-" * (max_name_length + 1)}\n'
        print(return_message)

    color_map = await get_colors_for_tasks(session, user_id)
    colors = [color_map.get(k, "gray") for k in list(result.keys())[:-1]]

    plt.figure(figsize=(8, 8))
    plt.pie(
        [float(i.total_seconds()) for i in list(result.values())[:-1]],
        labels=list(result.keys())[:-1],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
    )
    plt.axis("equal")
    file_path = "services/stats.png"
    plt.savefig(file_path, format='png', bbox_inches="tight")

    return return_message, file_path


# Функция для форматирования времени
async def get_formatted_time(delta: timedelta) -> str:
    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)
    seconds = int(delta.total_seconds() % 60)

    formatted_time = f'{hours:02}:{minutes:02}:{seconds:02}'
    return formatted_time


# Функция для получения цвета задачи из базы
async def get_colors_for_tasks(session: AsyncSession, db_user_id: int) -> dict:
    tasks = await orm_get_tasks(session, db_user_id)
    # Берем цвета из списка табло на случай если не заполнен цвет в базе
    colors = list(x[4:] for x in TABLEAU_COLORS)
    color_map = {}
    color_index = 0
    for task in tasks:
        if getattr(task, 'color', None) is None:
            task.color = colors[color_index]
            # Циклическое использование цветов
            color_index = (color_index + 1) % 20
        color_map[task.name] = task.color
    return color_map

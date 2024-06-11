from datetime import datetime, timedelta

from matplotlib import pyplot as plt
from matplotlib.colors import CSS4_COLORS
import matplotlib.dates as mdates

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
        filter(Works.user_id == user_id))
    # Фильтр по дате, где дата больше или равно текущий год, месяц, день
    today = datetime.today()
    if period == 'today':
        multiplier = 1
        start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)  # Начало текущего дня
        end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59)  # Конец текущего дня

        stats_query = query.filter(
            Works.start_time >= start_of_day,
            Works.end_time <= end_of_day
        )
    elif period == 'yesterday':
        multiplier = 1
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
        multiplier = today.weekday() + 1
        # цель умножается на количество дней с начала недели
        stats_query = query.filter(
            Works.start_time >= start_of_week,
            Works.end_time <= datetime.today()
        )
    else:
        start_of_month = datetime(today.year, today.month, 1)
        multiplier = (datetime.today() - start_of_month).days
        # цель умножается на количество дней с начала месяца
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
    result.setdefault(LEXICON_RU['total'], sum(result.values(), timedelta()))
    targets_map = await get_targets_for_tasks(session, user_id)
    # Цели выполнения задач будут добавлены в строку сообщения
    max_name_length = max(len(k) for k in result.keys())
    for i, (k, v) in enumerate(result.items()):
        padding = ' ' * (max_name_length - len(k))
        target_pad = ' ' * (max_name_length - 4)
        # Форматируем сообщение
        if targets_map.get(k, '') == '':
            return_message += (f'<code>{LEXICON_RU["not_set"]} {k}{padding}: {await get_formatted_time(v)}\n'
                               f'{LEXICON_RU["target"]}{target_pad}: {await get_formatted_time(timedelta(minutes=0))}</code>\n')
        else:
            return_message += (f'<code>{LEXICON_RU[await goal_achieved(v, targets_map[k])]} {k}{padding}: '
                               f'{await get_formatted_time(v)}\n{LEXICON_RU["target"]}{target_pad}: '
                               f'{await get_formatted_time(timedelta(minutes=targets_map.get(k, "") * multiplier))}</code>\n')
        if i == len(result) - 2:
            return_message += f'{"-" * (max_name_length + 1)}\n'

    # Создание кругового графика
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

    await session.commit()
    if period == 'today':
        file_path = await plot_gantt_chart(session, user_id, color_map)
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
    # Берем цвета из списка css4 на случай если не заполнен цвет в базе
    colors = list(CSS4_COLORS)
    color_map = {}
    color_index = 0
    for task in tasks:
        if getattr(task, 'color', None) is None:
            task.color = colors[color_index]
            # Циклическое использование цветов
            color_index = (color_index + 1) % 20
        color_map[task.name] = task.color
    return color_map


async def get_targets_for_tasks(session: AsyncSession, db_user_id: int) -> dict:
    # Получаем цели по времени выполнения задач, если они заданы
    tasks = await orm_get_tasks(session, db_user_id)
    tasks_with_targets = {}
    for task in tasks:
        if getattr(task, 'target_time', None) is None:
            task.target_time = ''
        tasks_with_targets[task.name] = task.target_time
    return tasks_with_targets


async def goal_achieved(spend_time: timedelta, target_time: int) -> str:
    if target_time <= spend_time.total_seconds() / 60:
        return 'achieved'
    else:
        return 'not_achieved'


async def plot_gantt_chart(session: AsyncSession, db_user_id: int, color_map, fig_size=(12, 2), bar_height=1) -> str:
    today = datetime.today()
    start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)
    query = (select(
        Task.name,
        Works.start_time,
        Works.end_time,
    ).join(Task, Task.id == Works.task_id).order_by(Task.name).
             filter(Works.user_id == db_user_id, Works.start_time > start_of_day))
    stats = await session.execute(query)

    tasks = []
    start_times = []
    end_times = []

    for stat in stats:
        task_name = stat[0]
        start_time = stat[1]
        end_time = stat[2]

        tasks.append(task_name)
        start_times.append(start_time)
        end_times.append(end_time)

    # Построение временной шкалы
    fig, ax = plt.subplots(figsize=fig_size)

    # Установка формата дат на оси X
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Добавление полосок задач на временную шкалу на одной линии
    y_pos = 0.5  # Позиция по оси Y для всех задач
    for i, task in enumerate(tasks):
        start = mdates.date2num(start_times[i])
        end = mdates.date2num(end_times[i])
        duration = end - start
        # Получаю цвет из color_map
        task_color = color_map.get(task, (0, 0, 0, 0))

        ax.broken_barh([(start, duration)], (0, bar_height), facecolors=task_color)
        # Добавление аннотаций задач
        ax.annotate(task, (start + duration / 2, 0.5), color='black',
                    fontsize=7, ha='center', va='center', rotation=90)

    # Настройка осей
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xlabel(LEXICON_RU['time'])
    ax.set_ylabel(LEXICON_RU['tasks'])
    ax.set_title(LEXICON_RU['time_line'])
    plt.gcf().autofmt_xdate()

    file_path = "services/gantt_chart.png"
    plt.savefig(file_path, format='png', bbox_inches="tight")

    return file_path

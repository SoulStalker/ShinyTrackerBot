from datetime import datetime, timedelta

from sqlalchemy import select, update, delete, null, extract, func, case, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from database.models import User, Task, Works
from lexicon.lexicon import LEXICON_RU


# Функция возвращает пользователя по его telegram ID
async def orm_get_user_by_id(session: AsyncSession, user_id: int) -> User:
    query = select(User).where(User.username == user_id)
    users = await session.execute(query)
    user = users.scalars().first()
    return user


# Функция добавления нового пользователя
async def orm_add_user(session: AsyncSession, user_id: int) -> None:
    obj = User(
        username=user_id,
    )
    session.add(obj)
    await session.commit()


# Функция добавления задачи
async def orm_add_task(session: AsyncSession, data: dict) -> None:
    obj = Task(
        user_id=data['user_id'],
        name=data['task_name'],
    )
    session.add(obj)
    await session.commit()


# Функция получения списка задач
async def orm_get_tasks(session: AsyncSession, user_id: int) -> list[Task]:
    query = select(Task.name).where(user_id == user_id)
    tasks = await session.execute(query)
    tasks = tasks.scalars().all()
    return list(tasks)


# Функция удаляет задачу из базы по названию
async def orm_remove_task(session: AsyncSession, task_name: str) -> str:
    success = LEXICON_RU['success']
    try:
        query = delete(Task).where(Task.name == task_name)
        await session.execute(query)
        await session.commit()
    except Exception as e:
        success = e
    return success


# Функция изменяет задачу из базы по названию
async def orm_edit_task(session: AsyncSession, task: dict) -> None:
    query = (update(Task).where(
        (Task.user_id == task['user_id']) & (Task.name == task['old_task_name'])
    ).
             values(name=task['new_task_name']))
    await session.execute(query)
    await session.commit()


# Функция записывает начало работы задачи
async def orm_update_work(session: AsyncSession, task_name: str, user_id: int) -> None:
    tasks = await session.execute(select(Task.id).where(Task.name == task_name))
    task_id = tasks.scalars().first()
    obj = Works(
        user_id=user_id,
        task_id=task_id,
        start_time=datetime.utcnow()
    )
    session.add(obj)
    await session.commit()


# Функция записывает время окончания задачи
# Так как не должно быть незаконченных задач сразу закрываем все незаконченные
async def orm_stop_work(session: AsyncSession, user_id: int) -> None:
    query = (update(Works).where(
        (Works.user_id == user_id) & (Works.end_time == None)
    ).
             values(end_time=datetime.utcnow()))
    await session.execute(query)
    await session.commit()

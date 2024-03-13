from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Task
from lexicon.lexicon import LEXICON_RU


async def orm_get_user_by_id(session: AsyncSession, user_id: int) -> User:
    query = select(User).where(User.username == user_id)
    users = await session.execute(query)
    user = users.scalars().first()
    return user


async def orm_add_user(session: AsyncSession, user_id: int) -> None:
    obj = User(
        username=user_id,
    )
    session.add(obj)
    await session.commit()


async def orm_add_task(session: AsyncSession, data: dict) -> None:
    obj = Task(
        user_id=data['user_id'],
        name=data['task_name'],
    )
    session.add(obj)
    await session.commit()


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
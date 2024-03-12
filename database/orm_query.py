from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Task


async def orm_get_user_by_id(session: AsyncSession, user_id: str) -> User:
    query = select(User).where(User.username == user_id)
    users = await session.execute(query)
    user = users.scalars().first()
    return user


async def orm_add_user(session: AsyncSession, user_id: str) -> None:
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

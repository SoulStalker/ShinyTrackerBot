import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import load_config
from keyboards.set_menu import set_main_menu
from handlers import other_handlers, user_handlers
from middlewares.outer import ShadowBanMiddleware, DbMiddleware
from database.enginge import drop_tables, create_tables, session_maker

storage = MemoryStorage()


# класс для состояний
class FSMGetTaskName(StatesGroup):
    # Состояние для ожидания называния новой задачи
    fill_task_name = State()
    # Состояние для ожидания нового названия
    set_task_name = State()
    # Состояние для ожидания нового цвета
    set_task_color = State()
    # Состояние для ожидания новой длительности
    set_work_duration_time = State()
    set_break_duration_time = State()


async def main():
    config = load_config('.env')
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage)
    await set_main_menu(bot)
    # # Создаем базу
    # await drop_tables()
    # await create_tables()

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # Подключается мидлваря для блокировки всех кроме админа
    dp.update.middleware(ShadowBanMiddleware(config.tg_bot.admin_ids))
    # Мидлваря для подключения базы данных
    dp.update.middleware(DbMiddleware(session_pool=session_maker))
    # Passing accumulated updates and starting polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

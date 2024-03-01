import asyncio

from aiogram import Bot, Dispatcher

from config_data.config import load_config
from keyboards.set_menu import set_main_menu
from handlers import other_handlers, user_handlers
from middlewares.outer import ShadowBanMiddleware

# SUPER_ADMIN = config.tg_bot.admin_ids[0]


async def main():
    config = load_config('.env')
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher()
    await set_main_menu(bot)

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # Подключается мидлваря для блокировки всех кроме админа
    dp.update.middleware(ShadowBanMiddleware(config.tg_bot.admin_ids))

    # Passing accumulated updates and starting polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
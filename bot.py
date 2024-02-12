from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config_data.config import load_config
from keyboards.set_menu import set_main_menu
from lexicon.lexicon import LEXICON_RU

config = load_config('.env')

SUPER_ADMIN = config.tg_bot.admin_ids[0]


bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
dp = Dispatcher()
set_main_menu(bot)


@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'])


@dp.message(Command('help'))
async def help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


if __name__ == '__main__':
    dp.run_polling(bot)
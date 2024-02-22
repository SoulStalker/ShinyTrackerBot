from aiogram import Router
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import LEXICON_RU

from database.database import users_db

router = Router()


# Handler for messages passed by other handlers
@router.message()
async def send_message(message: Message):
    await message.answer(text=LEXICON_RU['other_answer'])


@router.callback_query()
async def callback_query(callback: CallbackQuery):
    text = callback.data[:-3]
    cats = users_db[callback.from_user.id]['categories']
    await callback.message.answer(f"{callback.data[-3:] == 'del'}, {text}, {cats}")
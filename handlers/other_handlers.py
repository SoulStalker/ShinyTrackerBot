from aiogram import Router
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import LEXICON_RU
from services.services import bot_messages_ids

router = Router()


# Handler for messages passed by other handlers
@router.message()
async def send_message(message: Message):
    msg = await message.answer(text=LEXICON_RU['other_answer'])
    bot_messages_ids.setdefault(message.chat.id, []).append(msg.message_id)
    bot_messages_ids.setdefault(message.chat.id, []).append(message.message_id)


@router.callback_query()
async def callback_query(callback: CallbackQuery):
    text = callback.data
    await callback.message.answer(f"{text}")
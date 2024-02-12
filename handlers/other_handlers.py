from aiogram import Router
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU

router = Router()


# Handler for messages passed by other handlers
@router.message()
async def send_message(message: Message):
    await message.answer(text=LEXICON_RU['other_answer'])
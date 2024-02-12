from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from keyboards.keyboards import common_keyboard
from lexicon.lexicon import LEXICON_RU


router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'], reply_markup=common_keyboard)


@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'], reply_markup=common_keyboard)


@router.message(Command('support'))
async def support_command(message: Message):
    await message.answer(text=LEXICON_RU['/support'], reply_markup=common_keyboard)


@router.message(Command('contacts'))
async def contacts_command(message: Message):
    await message.answer(text=LEXICON_RU['/contacts'], reply_markup=common_keyboard)


@router.message(F.text == LEXICON_RU['add_category'])
async def add_category(message: Message):
    await message.answer("Добавляем категорию", reply_markup=common_keyboard)


@router.message(F.text == LEXICON_RU['delete_category'])
async def delete_category(message: Message):
    await message.answer("Удаляем категорию", reply_markup=common_keyboard)


@router.message(F.text == LEXICON_RU['choose_category'])
async def choose_category(message: Message):
    await message.answer("Выбираем категорию", reply_markup=common_keyboard)


@router.message(F.text == LEXICON_RU['statistics'])
async def statistics(message: Message):
    await message.answer("Тут выводим статистику", reply_markup=common_keyboard)
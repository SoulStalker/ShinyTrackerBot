from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from keyboards.keyboards import common_keyboard, categories_keyboard, create_add_category_kb
from lexicon.lexicon import LEXICON_RU
from services.services import add_category

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
    await message.answer(text=LEXICON_RU['/add_category'], reply_markup=common_keyboard)


@router.message(F.text == LEXICON_RU['delete_category'])
async def delete_category(message: Message):
    await message.answer("Удаляем категорию", reply_markup=common_keyboard)


@router.message(F.text == LEXICON_RU['choose_category'])
async def choose_category(message: Message):
    await message.answer("Выбери категорию", reply_markup=categories_keyboard)


@router.message(F.text == LEXICON_RU['statistics'])
async def statistics(message: Message):
    await message.answer("Тут выводим статистику", reply_markup=common_keyboard)


@router.callback_query(F.data == 'cat_1_pressed')
async def cat_1_pressed(callback: CallbackQuery):
    if callback.data != 'cat_1_pressed':
        await callback.message.edit_text(text='cat 1 pressed', reply_markup=callback.message.reply_markup)
    await callback.answer(text="WOW 1")


@router.callback_query(F.data == 'cat_2_pressed')
async def cat_2_pressed(callback: CallbackQuery):
    if callback.data != 'cat_2_pressed':
        await callback.message.edit_text(text='cat 2 pressed', reply_markup=callback.message.reply_markup)
    await callback.answer(text="WOW 2", show_alert=True)


@router.message(lambda x: len(x.text) < 20 and x.text.startswith('.'))
async def add_cat(message: Message):
    await message.answer(
        text=f'Добавляется категория {message.text[1:]}',
        reply_markup=create_add_category_kb(message.text[1:]),
    )
    await message.answer()

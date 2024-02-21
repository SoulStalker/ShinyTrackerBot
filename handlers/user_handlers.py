from copy import deepcopy

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from keyboards.keyboards import common_keyboard, categories_keyboard, create_add_category_kb, create_edit_category_kb
from lexicon.lexicon import LEXICON_RU
from database.database import users_db, user_dict_template

router = Router()
last_category = None


@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'], reply_markup=common_keyboard)
    if message.from_user.id not in users_db:
        users_db[message.from_user.id] = deepcopy(user_dict_template)


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


@router.message(F.text == LEXICON_RU['edit_categories'])
async def edit_categories(message: Message):
    if users_db[message.from_user.id]['categories']:
        await message.answer(
            text=LEXICON_RU['/edit_categories'],
            reply_markup=create_edit_category_kb(
                *users_db[message.from_user.id]['categories']
            )
        )
    else:
        await message.answer(text=LEXICON_RU['no_category'])


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
    global last_category
    last_category = message.text[1:]
    if message.from_user.id in users_db.keys():
        await message.answer(
            text=f'Добавляется категория {last_category}',
            reply_markup=create_add_category_kb(),
        )
    else:
        await message.answer(text=LEXICON_RU['no_user'])


# Этот хендлер срабатывает на кнопку отмена в инлайне добавления категории
@router.callback_query(F.data == 'cancel_add')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['/add_category'])
    await callback.answer()


# Этот хендлер срабатывает на кнопку добавить в инлайне добавления категории
@router.callback_query(F.data == 'really_add')
async def process_really_add_press(callback: CallbackQuery):
    users_db[callback.from_user.id]['categories'].add(
        last_category
    )
    await callback.answer(
        text=f"{LEXICON_RU['category added']} {last_category}",
        show_alert=True
    )



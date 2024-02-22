from copy import deepcopy

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery

from keyboards.keyboards import (common_keyboard, create_categories_keyboard,
                                 create_add_category_kb, create_edit_category_kb,
                                 create_stop_task_kb, create_start_yes_no_kb)
from lexicon.lexicon import LEXICON_RU
from database.database import users_db, user_dict_template
from filters.filters import IsUsersCategories, ShowUsersCategories, IsStopTasks

router = Router()
last_category = None


# Этот хендлер срабатывает на команду /start и создает базу данных
@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=create_start_yes_no_kb())
    if message.from_user.id not in users_db:
        users_db[message.from_user.id] = deepcopy(user_dict_template)


@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer(
        text=LEXICON_RU['/help'],
        reply_markup=create_start_yes_no_kb())


@router.message(Command('support'))
async def support_command(message: Message):
    await message.answer(text=LEXICON_RU['/support'], reply_markup=common_keyboard)


@router.message(Command('contacts'))
async def contacts_command(message: Message):
    await message.answer(text=LEXICON_RU['/contacts'], reply_markup=common_keyboard)


@router.message(F.text == LEXICON_RU['add_category'])
async def add_category(message: Message):
    await message.answer(text=LEXICON_RU['/add_category'], reply_markup=common_keyboard)


# Этот хендлер срабатывает на нажатие кнопки "Редактировать категории"
# в ответ выдается инлайн клавиатура с категориями
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
        await message.answer(text=LEXICON_RU['no_category'], reply_markup=common_keyboard)


@router.message(F.text == LEXICON_RU['choose_category'])
async def choose_category(message: Message):
    await message.answer(
        text=LEXICON_RU['/choose_category'],
        reply_markup=create_categories_keyboard(
            2,
            *users_db[message.from_user.id]['categories']))


@router.message(F.text == LEXICON_RU['statistics'])
async def statistics(message: Message):
    await message.answer("Тут выводим статистику", reply_markup=common_keyboard)


# Этот хендлер срабатывает на сообщения которые начинаются с точки. Пока фильтрую так
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
@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['/add_category'])
    await callback.answer(reply_markup=common_keyboard)


# Этот хендлер срабатывает на кнопку добавить в инлайне добавления категории
@router.callback_query(F.data == 'really_add')
async def process_really_add_press(callback: CallbackQuery):
    users_db[callback.from_user.id]['categories'].add(
        last_category
    )
    await callback.message.answer(
        text=f"{LEXICON_RU['category added']} {last_category}\n"
             f"{LEXICON_RU['another category']}"
             f"{LEXICON_RU['/add_category']}",
        reply_markup=common_keyboard
    )


# Этот хендлер срабатывает на нажатие на категорию в инлайне редактирования категорий
@router.callback_query(IsUsersCategories())
async def process_press_categories(callback: CallbackQuery):
    users_db[callback.from_user.id]['categories'].remove(callback.data[:-3])
    await callback.message.edit_text(
        text=LEXICON_RU['/edit_categories'],
        reply_markup=create_edit_category_kb(
            *users_db[callback.from_user.id]['categories'])
    )
    await callback.answer(
        text=f"{LEXICON_RU['category_deleted']} {callback.data[:-3]}")


# Этот хендлер срабатывает на нажатие на категорию в списке и запускает работу по задаче
@router.callback_query(ShowUsersCategories())
async def process_choose_category(callback: CallbackQuery):
    chosen_category = callback.data
    await callback.message.edit_text(
        text=f"{LEXICON_RU['start_work']} {chosen_category}{LEXICON_RU['stop_work']}",
        reply_markup=create_stop_task_kb(chosen_category)
    )


# Этот хендлер срабатывает на нажатие остановки задачи
@router.callback_query(IsStopTasks())
async def process_stop(callback: CallbackQuery):
    await callback.message.answer(
        text=LEXICON_RU['/choose_category'],
        reply_markup=create_categories_keyboard(
            2,
            *users_db[callback.from_user.id]['categories'])
    )
    await callback.answer(
        text=f"{LEXICON_RU['task for category']} {callback.data[:-5]} {LEXICON_RU['is stopped']}")


# Этот хендлер срабатывает на ответ "Да" в начале работы бота
@router.callback_query(F.data == 'yes')
async def process_yes(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['lets_start']
    )
    await callback.answer(
        text=LEXICON_RU['yes'],
        reply_markup=common_keyboard
    )
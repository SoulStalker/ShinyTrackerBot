from email import message

from sqlalchemy import select

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.keyboards import (common_keyboard, create_categories_keyboard,
                                 create_add_category_kb, create_edit_category_kb,
                                 create_stop_task_kb, create_start_yes_no_kb)
from lexicon.lexicon import LEXICON_RU
from database.database import users_db
from database.models import User
from filters.filters import IsUsersCategories, ShowUsersCategories, IsStopTasks
from database.orm_query import orm_get_user_by_id, orm_add_user, orm_add_task, orm_get_tasks

router = Router()
last_category = None


# Этот хендлер срабатывает на команду /start и создает пользователя в базе данных
@router.message(CommandStart())
async def start_command(message: Message, session: AsyncSession):
    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=create_start_yes_no_kb())
    if not await orm_get_user_by_id(session, message.from_user.id):
        await orm_add_user(session, message.from_user.id)


@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer(
        text=LEXICON_RU['/help'],
        reply_markup=create_start_yes_no_kb())


@router.message(Command('support'))
async def support_command(message: Message):
    await message.answer(
        text=LEXICON_RU['/support'],
        reply_markup=common_keyboard)


@router.message(Command('contacts'))
async def contacts_command(message: Message):
    await message.answer(
        text=LEXICON_RU['/contacts'],
        reply_markup=common_keyboard)


@router.callback_query(F.data == 'add_category')
async def add_category(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['/add_category'],
        reply_markup=common_keyboard)


# Этот хендлер срабатывает на нажатие кнопки "Редактировать задачи"
# в ответ выдается инлайн клавиатура с задачами
@router.callback_query(F.data == 'edit_categories')
async def edit_categories(callback: CallbackQuery):
    if users_db[callback.from_user.id]['categories']:
        await callback.message.edit_text(
            text=LEXICON_RU['/edit_categories'],
            reply_markup=create_edit_category_kb(
                *users_db[callback.from_user.id]['categories']
            )
        )
    else:
        await callback.message.edit_text(
            text=LEXICON_RU['no_category'],
            reply_markup=common_keyboard)


# Этот хендлер срабатывает на инлайн кнопку "Задача"
@router.callback_query(F.data == 'choose_category')
async def choose_category(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    tasks = await orm_get_tasks(session, user.id)
    await callback.message.edit_text(
        text=LEXICON_RU['/choose_category'],
        reply_markup=create_categories_keyboard(
            2,
            *tasks))


@router.callback_query(F.data == 'statistics')
async def statistics(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Тут выводим статистику",
        reply_markup=common_keyboard)


# Этот хендлер срабатывает на сообщения которые начинаются с точки. Пока фильтрую так
@router.message(lambda x: len(x.text) < 20 and x.text.startswith('.'))
async def add_cat(message: Message, session: AsyncSession):
    global last_category
    last_category = message.text[1:]
    if await orm_get_user_by_id(session, message.from_user.id):
        await message.answer(
            text=f'{LEXICON_RU["/ads_task"]} {last_category}',
            reply_markup=create_add_category_kb(),
        )
    else:
        await message.answer(text=LEXICON_RU['no_user'])


# Этот хендлер срабатывает на кнопку отмена в инлайне добавления задачи
@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['/add_category'],
        reply_markup=common_keyboard
    )


# Этот хендлер срабатывает на кнопку добавить в инлайне добавления задачи
@router.callback_query(F.data == 'really_add')
async def process_really_add_press(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    task = {'user_id': user.id, 'task_name': last_category}
    await orm_add_task(session, task)
    await callback.message.edit_text(
        text=f"{LEXICON_RU['category added']} {last_category}\n"
             f"{LEXICON_RU['another category']}"
             f"{LEXICON_RU['/add_category']}",
        reply_markup=common_keyboard
    )


# Этот хендлер срабатывает на нажатие на задачу в инлайне редактирования задач
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


# Этот хендлер срабатывает на нажатие на задачу в списке и запускает работу по задаче
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
    await callback.message.edit_text(
        text=LEXICON_RU['/choose_category'],
        reply_markup=create_categories_keyboard(
            2,
            *users_db[callback.from_user.id]['categories'])
    )
    await callback.message.edit_text(
        text=f"{LEXICON_RU['task for category']} {callback.data[:-5]} "
             f"{LEXICON_RU['is stopped']}\n\n{LEXICON_RU['/choose_category']}",
        reply_markup=create_categories_keyboard(
            2,
            *users_db[callback.from_user.id]['categories'])
    )


# Этот хендлер срабатывает на ответ "Да" в начале работы бота
@router.callback_query(F.data == 'yes')
async def process_yes(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['lets_start'],
        reply_markup=common_keyboard
    )

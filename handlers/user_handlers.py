from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.keyboards import (common_keyboard, create_categories_keyboard, create_add_category_kb,
                                 create_del_tasks_kb, create_stop_task_kb, create_start_yes_no_kb,
                                 create_stats_kb, create_cancel_kb, create_del_or_edit_tasks_kb,
                                 create_edit_tasks_kb)
from lexicon.lexicon import LEXICON_RU
from filters.filters import (IsUsersDelCategories, ShowUsersCategories, IsStopTasks, IsInPeriods,
                             IsUsersEditCategories)
from database.orm_query import (orm_get_user_by_id, orm_add_user, orm_add_task, orm_get_tasks,
                                orm_remove_task, orm_update_work, orm_stop_work, orm_edit_task)
from services.services import orm_get_day_stats
from bot import FSMGetTaskName

router = Router()
new_task_name = None
old_task_name = None


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
async def add_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON_RU['/add_category'],
        reply_markup=create_cancel_kb())
    await state.set_state(FSMGetTaskName.fill_task_name)


# Этот хендлер срабатывает на нажатие кнопки "Редактировать задачи"
# в ответ выдается инлайн клавиатура с вопросами удалить или изменить задачу
@router.callback_query(F.data == 'edit_categories')
async def edit_categories(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['del_or_edit_task'],
        reply_markup=create_del_or_edit_tasks_kb()
    )


# Этот хендлер срабатывает на нажатие кнопки "Удалить задачи"
# в ответ выдается инлайн клавиатура с задачами
@router.callback_query(F.data == 'del_task')
async def del_task(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    tasks = await orm_get_tasks(session, user.id)
    if tasks:
        await callback.message.edit_text(
            text=LEXICON_RU['/edit_categories'],
            reply_markup=create_del_tasks_kb(
                *tasks
            )
        )
    else:
        await callback.message.edit_text(
            text=LEXICON_RU['no_category'],
            reply_markup=common_keyboard)


# Этот хендлер срабатывает на нажатие кнопки "Изменить задачи"
# в ответ выдается инлайн клавиатура с задачами
@router.callback_query(F.data == 'edit_task')
async def del_task(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    tasks = await orm_get_tasks(session, user.id)
    if tasks:
        await callback.message.edit_text(
            text=LEXICON_RU['chose_task_for_edit'],
            reply_markup=create_edit_tasks_kb(
                *tasks
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


# Этот хендлер срабатывает на нажатие кнопки статистики и возвращает клавиатуру с периодами
@router.callback_query(F.data == 'statistics')
async def statistics(callback: CallbackQuery):
    await callback.message.edit_text(
        # ,
        text=LEXICON_RU['stats'],
        reply_markup=create_stats_kb(width=2))


# Этот хендлер срабатывает на нажатие кнопки month, то есть выводит статистику за месяц
@router.callback_query(IsInPeriods())
async def process_yesterday_statistics(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    stats = await orm_get_day_stats(session, user.id, callback.data)
    await callback.message.edit_text(
        text=f"{LEXICON_RU['stats_for']} {LEXICON_RU[callback.data].lower()}\n\n{stats}",
        reply_markup=create_stats_kb()
    )


# Этот хендлер срабатывает на сообщения в FSM состоянии fill_task_name
@router.message(StateFilter(FSMGetTaskName.fill_task_name), F.text.isalpha())
async def add_cat(message: Message, session: AsyncSession, state: FSMContext):
    global new_task_name
    await state.update_data(task_name=message.text)
    state_data = await state.get_data()
    new_task_name = state_data['task_name']
    if await orm_get_user_by_id(session, message.from_user.id):
        await message.answer(
            text=f'{LEXICON_RU["/ads_task"]} {new_task_name}',
            reply_markup=create_add_category_kb(),
        )
    else:
        await message.answer(text=LEXICON_RU['no_user'])


# Этот хендлер срабатывает на кнопку отмена в инлайне добавления задачи в FSM состоянии fill_task_name
@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON_RU['choose_action'],
        reply_markup=common_keyboard
    )
    await state.clear()


# Этот хендлер срабатывает на кнопку добавить в инлайне добавления задачи в FSM состоянии fill_task_name
@router.callback_query(StateFilter(FSMGetTaskName.fill_task_name), F.data == 'really_add')
async def process_really_add_press(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    task = {'user_id': user.id, 'task_name': new_task_name}
    if new_task_name in await orm_get_tasks(session, user.id):
        await callback.message.edit_text(LEXICON_RU['task_exist'])
    else:
        await orm_add_task(session, task)
        await callback.message.edit_text(
            text=f"{LEXICON_RU['category added']} {new_task_name}\n",
            reply_markup=common_keyboard
        )
        await state.clear()


# Этот хендлер срабатывает на ввод некорректных данных в состоянии в FSM состоянии fill_task_name
@router.message(StateFilter(FSMGetTaskName.fill_task_name))
async def warning_incorrect_task(message: Message):
    await message.answer(
        text=LEXICON_RU['incorrect_task_name'],
        reply_markup=create_cancel_kb(),
    )


# Этот хендлер срабатывает на нажатие на задачу в инлайне удаление задач
@router.callback_query(IsUsersDelCategories())
async def process_press_categories(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    await orm_remove_task(session, callback.data[:-3])
    new_tasks = await orm_get_tasks(session, user.id)
    await callback.message.edit_text(
        text=LEXICON_RU['/edit_categories'],
        reply_markup=create_del_tasks_kb(*new_tasks)
    )
    await callback.answer(
        text=f"{LEXICON_RU['category_deleted']} {callback.data[:-3]}")


# Этот хендлер срабатывает на нажатие на задачу в инлайне редактирования задач
@router.callback_query(IsUsersEditCategories())
async def process_press_categories(callback: CallbackQuery, state: FSMContext):
    global old_task_name
    old_task_name = callback.data[:-4]
    await callback.message.edit_text(
        text=f"{LEXICON_RU['new_task_name']} {callback.data[:-4]}",
    )
    await state.set_state(FSMGetTaskName.set_task_name)


# Этот хендлер срабатывает на сообщения в FSM состоянии set_task_name
@router.message(StateFilter(FSMGetTaskName.set_task_name), F.text.isalpha())
async def edit_cat(message: Message, session: AsyncSession, state: FSMContext):
    global new_task_name
    await state.update_data(task_name=message.text)
    state_data = await state.get_data()
    new_task_name = state_data['task_name']
    if await orm_get_user_by_id(session, message.from_user.id):
        await message.answer(
            text=f'{LEXICON_RU["new_name_of_task"]} {new_task_name}',
            reply_markup=create_start_yes_no_kb(),
        )
    else:
        await message.answer(text=LEXICON_RU['no_user'])


# Этот хендлер срабатывает на кнопку изменить в инлайне изменения задачи в FSM состоянии set_task_name
@router.callback_query(StateFilter(FSMGetTaskName.set_task_name), F.data == 'yes')
async def process_really_edit_press(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    task = {'user_id': user.id, 'old_task_name': old_task_name, 'new_task_name': new_task_name}
    if old_task_name in await orm_get_tasks(session, user.id):
        await callback.message.edit_text(LEXICON_RU['task_exist'])
        await orm_edit_task(session, task)
        await callback.message.edit_text(
            text=f"{LEXICON_RU['task_edited']} {new_task_name}\n",
            reply_markup=common_keyboard
        )
    else:
        await callback.message.edit_text(
            text=LEXICON_RU['task_not_exist'],
            reply_markup=common_keyboard
        )
    await state.clear()


# Этот хендлер срабатывает на нажатие на задачу в списке и запускает работу по задаче
@router.callback_query(ShowUsersCategories())
async def process_choose_category(callback: CallbackQuery, session: AsyncSession):
    chosen_task = callback.data
    user = await orm_get_user_by_id(session, callback.from_user.id)
    await orm_update_work(session, chosen_task, user.id)
    await callback.message.edit_text(
        text=f"{LEXICON_RU['start_work']} {chosen_task}{LEXICON_RU['stop_work']}",
        reply_markup=create_stop_task_kb(chosen_task)
    )


# Этот хендлер срабатывает на нажатие остановки задачи
@router.callback_query(IsStopTasks())
async def process_stop(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    tasks = await orm_get_tasks(session, user.id)
    await orm_stop_work(session, user.id)
    await callback.message.edit_text(
        text=LEXICON_RU['/choose_category'],
        reply_markup=create_categories_keyboard(
            2,
            *tasks)
    )
    await callback.message.edit_text(
        text=f"{LEXICON_RU['task for category']} {callback.data[:-5]} "
             f"{LEXICON_RU['is stopped']}\n\n{LEXICON_RU['/choose_category']}",
        reply_markup=create_categories_keyboard(
            2,
            *tasks)
    )


# Этот хендлер срабатывает на ответ "Да" в начале работы бота
@router.callback_query(F.data == 'yes')
async def process_yes(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['lets_start'],
        reply_markup=common_keyboard
    )

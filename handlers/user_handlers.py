import asyncio
from asyncio import create_task

from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.keyboards import (common_keyboard, create_tasks_keyboard, create_add_task_kb,
                                 create_del_tasks_kb, create_stop_task_kb, create_start_yes_no_kb,
                                 create_stats_kb, create_cancel_kb, create_del_or_edit_tasks_kb,
                                 create_edit_tasks_kb, create_service_kb)
from lexicon.lexicon import LEXICON_RU
from filters.filters import (IsUsersDelTasks, ShowUsersTasks, IsStopTasks, IsInPeriods,
                             IsUsersEditTasks)
from database.orm_query import (orm_get_user_by_id, orm_add_user, orm_add_task, orm_get_tasks,
                                orm_remove_task, orm_update_work, orm_stop_work, orm_edit_task,
                                orm_get_settings, orm_update_settings, orm_add_default_settings, orm_get_unclosed_work)
from services.services import orm_get_day_stats, bot_messages_ids
from bot import FSMGetTaskName

router = Router()
new_task_name = None
old_task_name = None


# Этот хендлер срабатывает на команду /start и создает пользователя в базе данных
@router.message(CommandStart())
async def start_command(message: Message, session: AsyncSession, bot: Bot):
    msg = await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=create_start_yes_no_kb())
    if not await orm_get_user_by_id(session, message.from_user.id):
        await orm_add_user(session, message.from_user.id)
    # bot_messages_ids.setdefault(message.chat.id, []).append(msg.message_id)
    bot_messages_ids.setdefault(message.chat.id, []).append(message.message_id)
    await process_do_the_chores(bot)


@router.message(Command('help'))
async def help_command(message: Message, bot: Bot):
    msg = await message.answer(
        text=LEXICON_RU['/help'],
        reply_markup=create_start_yes_no_kb())
    bot_messages_ids.setdefault(message.chat.id, []).append(msg.message_id)
    bot_messages_ids.setdefault(message.chat.id, []).append(message.message_id)
    await process_do_the_chores(bot)


@router.message(Command('service'))
async def support_command(message: Message, session: AsyncSession, bot: Bot):
    user = await orm_get_user_by_id(session, message.from_user.id)
    current_settings = await orm_get_settings(session, user.id)
    if current_settings is None:
        await orm_add_default_settings(session, user.id)
    await message.answer(
        text=f"{LEXICON_RU['/service']}"
             f"{LEXICON_RU['current_work_duration']} {current_settings.work_duration} {LEXICON_RU['minutes']}\n"
             f"{LEXICON_RU['current_break_duration']} {current_settings.break_duration} {LEXICON_RU['minutes']}",
        reply_markup=create_service_kb())


@router.message(Command('contacts'))
async def contacts_command(message: Message):
    await message.answer(
        text=LEXICON_RU['/contacts'],
        reply_markup=common_keyboard)


# Этот хендлер срабатывает на ответ "Да" в начале работы бота
@router.callback_query(F.data == 'yes', ~StateFilter(FSMGetTaskName.set_task_name))
async def process_yes(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['lets_start'],
        reply_markup=common_keyboard
    )


# Этот хендлер срабатывает на кнопку "Добавить задачу" и переводит бота в FSM состояние fill_task_name
@router.callback_query(F.data == 'add_task')
async def process_add_task_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON_RU['/add_task'],
        reply_markup=create_cancel_kb())
    await state.set_state(FSMGetTaskName.fill_task_name)


# Этот хендлер срабатывает на сообщения в FSM состоянии fill_task_name
@router.message(StateFilter(FSMGetTaskName.fill_task_name), F.text.isalpha())
async def process_add_task(message: Message, session: AsyncSession, state: FSMContext):
    global new_task_name
    await state.update_data(task_name=message.text)
    state_data = await state.get_data()
    new_task_name = state_data['task_name']
    if await orm_get_user_by_id(session, message.from_user.id):
        await message.answer(
            text=f'{LEXICON_RU["/ads_task"]} {new_task_name}',
            reply_markup=create_add_task_kb(),
        )
    else:
        await message.answer(text=LEXICON_RU['no_user'])


# Этот хендлер срабатывает на кнопку "добавить" в инлайне добавления задачи в FSM состоянии fill_task_name
@router.callback_query(StateFilter(FSMGetTaskName.fill_task_name), F.data == 'really_add')
async def process_really_add_press(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    task = {'user_id': user.id, 'task_name': new_task_name}
    if new_task_name in await orm_get_tasks(session, user.id):
        await callback.message.edit_text(LEXICON_RU['task_exist'])
    else:
        await orm_add_task(session, task)
        await callback.message.edit_text(
            text=f"{LEXICON_RU['task_added']} {new_task_name}\n",
            reply_markup=common_keyboard
        )
        await state.clear()


# Этот хендлер срабатывает на нажатие кнопки "Редактировать задачи"
# в ответ выдается инлайн клавиатура с вопросами удалить или изменить задачу
@router.callback_query(F.data == 'edit_categories')
async def process_edit_task(callback: CallbackQuery):
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
            text=LEXICON_RU['/edit_tasks'],
            reply_markup=create_del_tasks_kb(
                *tasks
            )
        )
    else:
        await callback.message.edit_text(
            text=LEXICON_RU['no_category'],
            reply_markup=common_keyboard)


# Этот хендлер срабатывает на нажатие на задачу в инлайне удаление задач
@router.callback_query(IsUsersDelTasks())
async def process_press_del_tasks(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    await orm_remove_task(session, callback.data[:-3])
    new_tasks = await orm_get_tasks(session, user.id)
    await callback.message.edit_text(
        text=LEXICON_RU['/edit_tasks'],
        reply_markup=create_del_tasks_kb(*new_tasks)
    )
    await callback.answer(
        text=f"{LEXICON_RU['task_deleted']} {callback.data[:-3]}")


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


# Этот хендлер срабатывает на нажатие на задачу в инлайне редактирования задач
@router.callback_query(IsUsersEditTasks())
async def process_press_edit_tasks(callback: CallbackQuery, state: FSMContext):
    global old_task_name
    old_task_name = callback.data[:-4]
    await callback.message.edit_text(
        text=f"{LEXICON_RU['new_task_name']} {callback.data[:-4]}",
    )
    await state.set_state(FSMGetTaskName.set_task_name)


# Этот хендлер срабатывает на сообщения в FSM состоянии set_task_name
@router.message(StateFilter(FSMGetTaskName.set_task_name), F.text.isalpha())
async def process_set_new_task_name(message: Message, session: AsyncSession, state: FSMContext):
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


# Этот хендлер срабатывает на ввод некорректных данных в состоянии в FSM состоянии fill_task_name и set_task_name
@router.message(StateFilter(FSMGetTaskName.fill_task_name, FSMGetTaskName.set_task_name))
async def warning_incorrect_task(message: Message):
    await message.answer(
        text=LEXICON_RU['incorrect_task_name'],
        reply_markup=create_cancel_kb(),
    )


# Этот хендлер срабатывает на инлайн кнопку "Задача"
@router.callback_query(F.data == 'choose_category')
async def process_choose_task(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    tasks = await orm_get_tasks(session, user.id)
    await callback.message.edit_text(
        text=LEXICON_RU['/choose_category'],
        reply_markup=create_tasks_keyboard(
            2,
            *tasks))


# Этот хендлер срабатывает на нажатие на задачу в списке и запускает работу по задаче
@router.callback_query(ShowUsersTasks())
async def process_start_task(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    chosen_task = callback.data
    user = await orm_get_user_by_id(session, callback.from_user.id)
    await orm_update_work(session, chosen_task, user.id)
    await callback.message.edit_text(
        text=f"{LEXICON_RU['start_work']} {chosen_task}{LEXICON_RU['stop_work']}",
        reply_markup=create_stop_task_kb(chosen_task)
    )
    current_settings = await orm_get_settings(session, user.id)
    period = current_settings.work_duration * 60
    await create_task(work_time_pomodoro(bot, session, callback.from_user.id, user.id, period, chosen_task))


# Этот хендлер срабатывает на нажатие остановки задачи
@router.callback_query(IsStopTasks())
async def process_stop(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    tasks = await orm_get_tasks(session, user.id)
    await orm_stop_work(session, user.id)
    await callback.message.edit_text(
        text=LEXICON_RU['/choose_category'],
        reply_markup=create_tasks_keyboard(
            2,
            *tasks)
    )
    await callback.message.edit_text(
        text=f"{LEXICON_RU['task for category']} {callback.data[:-5]} "
             f"{LEXICON_RU['is stopped']}\n\n{LEXICON_RU['/choose_category']}",
        reply_markup=create_tasks_keyboard(
            2,
            *tasks)
    )
    current_settings = await orm_get_settings(session, user.id)
    period = current_settings.break_duration * 60
    await create_task(rest_time_pomodoro(bot, session, callback.from_user.id, user.id, period))


# Этот хендлер срабатывает на нажатие кнопки статистики и возвращает клавиатуру с периодами
@router.callback_query(F.data == 'statistics')
async def statistics(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    stats = await orm_get_day_stats(session, user.id, "today")
    await callback.message.edit_text(
        text=f"{LEXICON_RU['stats_for']} <strong>{LEXICON_RU['today'].lower()}</strong>\n\n{stats}",
        reply_markup=create_stats_kb()
    )


# Этот хендлер срабатывает на нажатие кнопки с периодом, то есть выводит статистику за выбранные период
@router.callback_query(IsInPeriods())
async def process_period_statistics(callback: CallbackQuery, session: AsyncSession):
    user = await orm_get_user_by_id(session, callback.from_user.id)
    stats = await orm_get_day_stats(session, user.id, callback.data)
    await callback.message.edit_text(
        text=f"{LEXICON_RU['stats_for']} <strong>{LEXICON_RU[callback.data].lower()}</strong>\n\n{stats}",
        reply_markup=create_stats_kb()
    )


# Этот хендлер срабатывает на кнопку "Отмена" и сбрасывает состояние FSM
@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON_RU['choose_action'],
        reply_markup=common_keyboard
    )
    await state.clear()


# Этот хендлер срабатывает на кнопку "Задать длительность задачи" и переводит бота в FSM состояние set_work_duration_time
@router.callback_query(F.data == 'edit_work_time')
async def process_edit_work_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON_RU['give_new_work_time'],
        reply_markup=create_service_kb()
    )
    await state.set_state(FSMGetTaskName.set_work_duration_time)


# Этот хендлер срабатывает на с сообщения с цифрами в FSM состояние set_work_duration_time
@router.message(StateFilter(FSMGetTaskName.set_work_duration_time), F.text.isdigit())
async def process_get_work_time_from_message(message: Message, session: AsyncSession, state: FSMContext):
    user = await orm_get_user_by_id(session, message.from_user.id)
    current_settings = await orm_get_settings(session, user.id)
    await state.update_data(work_duration=message.text)
    state_data = await state.get_data()
    new_work_duration = state_data['work_duration']
    await orm_update_settings(session, user.id, work_duration=new_work_duration, break_duration=current_settings.break_duration)
    await message.answer(
        text=f'{LEXICON_RU["new_work_time"]} {new_work_duration} {LEXICON_RU["minutes"]}',
        reply_markup=create_service_kb(),
    )
    await state.clear()


# Этот хендлер срабатывает на кнопку "Задать длительность перерыва" и переводит бота в FSM состояние set_break_duration_time
@router.callback_query(F.data == 'edit_break_time')
async def process_edit_break_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON_RU['give_new_break_time'],
        reply_markup=create_service_kb()
    )
    await state.set_state(FSMGetTaskName.set_break_duration_time)


# Этот хендлер срабатывает на с сообщения с цифрами в FSM состояние set_break_duration_time
@router.message(StateFilter(FSMGetTaskName.set_break_duration_time), F.text.isdigit())
async def process_get_break_time_from_message(message: Message, session: AsyncSession, state: FSMContext):
    user = await orm_get_user_by_id(session, message.from_user.id)
    current_settings = await orm_get_settings(session, user.id)
    await state.update_data(break_duration=message.text)
    state_data = await state.get_data()
    new_break_duration = state_data['break_duration']
    await orm_update_settings(session, user.id, work_duration=current_settings.work_duration, break_duration=new_break_duration)
    await message.answer(
        text=f'{LEXICON_RU["new_break_duration"]} {new_break_duration} {LEXICON_RU["minutes"]}',
        reply_markup=create_service_kb(),
    )
    await state.clear()


# Этот хендлер срабатывает на ввод некорректных данных в состоянии в FSM состоянии set_work_duration_time b
# set_break_duration_time
@router.message(StateFilter(FSMGetTaskName.set_work_duration_time, FSMGetTaskName.set_break_duration_time))
async def warning_incorrect_duration(message: Message):
    await message.answer(
        text=LEXICON_RU['incorrect_duration'],
        reply_markup=create_cancel_kb(),
    )


# Функция для таймера рабочего времени
async def work_time_pomodoro(bot: Bot, session: AsyncSession, chat_id: int, user_id: int, delay: int, task_name: str) -> None:
    while True:
        await asyncio.sleep(delay)
        unclosed = await orm_get_unclosed_work(session, user_id)
        if unclosed is not None:
            text = f'{LEXICON_RU["time_to_close"]} {task_name}'
            await send_its_time_message(bot, session, user_id=chat_id, db_user=user_id, text=text, task_name=task_name)


# Функция для таймера перерыва
async def rest_time_pomodoro(bot: Bot, session: AsyncSession, chat_id: int, user_id: int, delay: int) -> None:
    while True:
        await asyncio.sleep(delay)
        unclosed = await orm_get_unclosed_work(session, user_id)
        if unclosed is None:
            text = f'{LEXICON_RU["time_to_work"]} {delay // 60} {LEXICON_RU["minutes"]}'
            await send_its_time_message(bot, session, user_id=chat_id, db_user=user_id, text=text)


# Функция для отправки сообщения, что пора на перерыв
async def send_its_time_message(bot: Bot, session: AsyncSession, user_id: int, db_user: int, text: str, task_name=None) -> None:
    if task_name:
        msg = await bot.send_message(user_id, text, reply_markup=create_stop_task_kb(task_name))
    else:
        tasks = await orm_get_tasks(session, db_user)
        msg = await bot.send_message(
            user_id,
            text=text,
            reply_markup=create_tasks_keyboard(
                2,
                *tasks)
        )
    bot_messages_ids.setdefault(msg.chat.id, []).append(msg.message_id)
    await process_do_the_chores(bot)


# функция для удаления старых сообщений
async def process_do_the_chores(bot: Bot):
    await asyncio.sleep(1200)
    for chat in bot_messages_ids.keys():
        for message_id in bot_messages_ids[chat]:
            try:
                await bot.delete_message(chat_id=chat, message_id=message_id)
            except Exception as err:
                print(err)
    bot_messages_ids.clear()

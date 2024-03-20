from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_RU


# Function for generating inline keyboards "on the fly"
def create_categories_keyboard(width: int = 2, *args: str | set, **kwargs: str) -> InlineKeyboardMarkup:
    # Initialize the builder
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    # Fill the list with buttons from args and kwargs arguments
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button
            ))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button
            ))

    # Unpack the list with buttons into the builder using the row method with the width parameter
    kb_builder.row(*buttons, width=width)
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['cancel'],
            callback_data='cancel'
        )
    )
    # Return the inline keyboard object
    return kb_builder.as_markup()


def create_common_keyboard(width: int = 2) -> InlineKeyboardMarkup:
    """
    Функция создает основную инлайн клавиатуру
    :param width:
    :return: InlineKeyboardMarkup
    """
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['add_category'],
            callback_data='add_category'
        ),
        InlineKeyboardButton(
            text=LEXICON_RU['edit_categories'],
            callback_data='edit_categories'
        ),
        InlineKeyboardButton(
            text=LEXICON_RU['choose_category'],
            callback_data='choose_category'
        ),
        InlineKeyboardButton(
            text=LEXICON_RU['statistics'],
            callback_data='statistics'
        ),
        width=width
    )
    return kb_builder.as_markup()


common_keyboard = create_common_keyboard(2)


def create_add_category_kb() -> InlineKeyboardMarkup:
    """
    Функция создает инлайн клавиатуру для добавления категорий
    :return: InlineKeyboardMarkup
    """
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['really_add_category'],
            callback_data='really_add'
        ),
        InlineKeyboardButton(
            text=LEXICON_RU['cancel_add_category'],
            callback_data='cancel'
        ),
        width=2
    )
    return kb_builder.as_markup()


def create_del_tasks_kb(*args: str) -> InlineKeyboardMarkup:
    """
    Функция создает инлайн клавиатуру для удаления задач
    :param args:
    :return: InlineKeyboardMarkup
    """
    kb_builder = InlineKeyboardBuilder()
    for button in sorted(args):
        kb_builder.row(InlineKeyboardButton(
            text=f'❌ {button}',
            callback_data=f'{button}del'
        ))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['cancel'],
            callback_data='cancel'
        )
    )
    return kb_builder.as_markup()


def create_edit_tasks_kb(*args: str) -> InlineKeyboardMarkup:
    """
    Функция создает инлайн клавиатуру для редактирования задач
    :param args:
    :return: InlineKeyboardMarkup
    """
    kb_builder = InlineKeyboardBuilder()
    for button in sorted(args):
        kb_builder.row(InlineKeyboardButton(
            text=f'📝 {button}',
            callback_data=f'{button}edit'
        ))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['cancel'],
            callback_data='cancel'
        )
    )
    return kb_builder.as_markup()


def create_stop_task_kb(task: str) -> InlineKeyboardMarkup:
    """
    Функция создает инлайн клавиатуру для остановки текущей задачи
    :param task:
    :return: InlineKeyboardMarkup
    """
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(
        text=f'{LEXICON_RU["/stop"]} {task}',
        callback_data=f'{task}_stop'
    ))
    return kb_builder.as_markup()


def create_start_yes_no_kb() -> InlineKeyboardMarkup:
    """
    Функция создает инлайн клавиатуру для начала работы
    :return: InlineKeyboardMarkup
    """
    kb_builder = InlineKeyboardBuilder()
    kb_builder.add(InlineKeyboardButton(
        text=LEXICON_RU['yes'],
        callback_data='yes'
    ))
    kb_builder.add(InlineKeyboardButton(
        text=LEXICON_RU['cancel'],
        callback_data='cancel'
    ))
    return kb_builder.as_markup()


def create_stats_kb(width: int = 4) -> InlineKeyboardMarkup:
    """
    Функция создает клавиатуру для вывода статистки
    по различным периодам
    :return: InlineKeyboardMarkup
    """
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['today'],
            callback_data='today'),
        InlineKeyboardButton(
            text=LEXICON_RU['yesterday'],
            callback_data='yesterday'),
        InlineKeyboardButton(
            text=LEXICON_RU['week'],
            callback_data='week'
        ),
        InlineKeyboardButton(
            text=LEXICON_RU['month'],
            callback_data='month'
        ),
        width=width
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['cancel'],
            callback_data='cancel'
        ))
    return kb_builder.as_markup()


def create_cancel_kb() -> InlineKeyboardMarkup:
    """
    Функция создает клавиатуру с одной кнопкой "Отмена"
    :return: InlineKeyboardMarkup
    """
    kb_builder = InlineKeyboardBuilder()
    kb_builder.add(InlineKeyboardButton(
        text=LEXICON_RU['cancel'],
        callback_data='cancel'
    ))
    return kb_builder.as_markup()


def create_del_or_edit_tasks_kb() -> InlineKeyboardMarkup:
    """
    Функция создает клавиатуру с вопросами удалять или изменять задачи
    :return: InlineKeyboardMarkup
    """
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_RU['del_task'],
            callback_data='del_task'),
        InlineKeyboardButton(
            text=LEXICON_RU['edit_task'],
            callback_data='edit_task')
        )
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['cancel'],
        callback_data='cancel'
    ))
    return kb_builder.as_markup()

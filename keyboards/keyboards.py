from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_RU

button_add_category = KeyboardButton(text=LEXICON_RU['add_category'])
button_edit_categories = KeyboardButton(text=LEXICON_RU['edit_categories'])
button_choose_category = KeyboardButton(text=LEXICON_RU['choose_category'])
button_statistics = KeyboardButton(text=LEXICON_RU['statistics'])

common_keyboard_builder = ReplyKeyboardBuilder()
common_keyboard_builder.row(button_choose_category, button_add_category,
                            button_edit_categories, button_statistics, width=2)


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
    # Return the inline keyboard object
    return kb_builder.as_markup()


common_keyboard: ReplyKeyboardMarkup = common_keyboard_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)


def create_add_category_kb() -> InlineKeyboardMarkup:
    """
    Функция создает инлайн клавиатуру для добавления категорий
    :return: InlineKeyboardMarkup:
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


def create_edit_category_kb(*args: str) -> InlineKeyboardMarkup:
    """
    Функция создает инлайн клавиатуру для редактирования категорий
    :param args:
    :return: InlineKeyboardMarkup
    """
    kb_builder = InlineKeyboardBuilder()
    for button in sorted(args):
        kb_builder.row(InlineKeyboardButton(
            text=button,
            callback_data=f'{button}del'
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

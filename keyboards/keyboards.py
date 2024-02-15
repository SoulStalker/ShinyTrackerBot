from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon import LEXICON_RU
from services.services import categories

button_add_category = KeyboardButton(text=LEXICON_RU['add_category'])
button_delete_category = KeyboardButton(text=LEXICON_RU['delete_category'])
button_choose_category = KeyboardButton(text=LEXICON_RU['choose_category'])
button_statistics = KeyboardButton(text=LEXICON_RU['statistics'])

common_keyboard_builder = ReplyKeyboardBuilder()
common_keyboard_builder.row(button_choose_category, button_add_category,
                            button_delete_category, button_statistics, width=2)

common_keyboard: ReplyKeyboardMarkup = common_keyboard_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)


big_button_1 = InlineKeyboardButton(
    text='Категория_1',
    callback_data='cat_1_pressed'
)

big_button_2 = InlineKeyboardButton(
    text='Категория_2',
    callback_data='cat_2_pressed'
)
categories_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[big_button_1], [big_button_2]])

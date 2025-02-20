from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON


# Функция формирования инлайн клавиатуры
def create_inline_kb(width: int,
                     *args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:

    # Инициализация билдера инлайн клавиатуры
    kb_builder = InlineKeyboardBuilder()
    # Список для кнопок
    buttons: list[InlineKeyboardButton] = []

    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON[button] if button in LEXICON else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    # Распаковка списка с кнопками в билдер методом row с параметров width
    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()
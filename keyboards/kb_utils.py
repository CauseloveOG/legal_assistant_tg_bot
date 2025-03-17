from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON


# Функция формирования инлайн клавиатуры
def create_inline_kb(width: int,
                     *args: str,
                     optional_button: list | None = None,
                     **kwargs: str) -> InlineKeyboardMarkup:

    # Инициализация билдера инлайн клавиатуры
    kb_builder = InlineKeyboardBuilder()
    # Список для кнопок
    buttons: list[InlineKeyboardButton] = []

    if optional_button:
        opt_buttons: list[InlineKeyboardButton] = []
        for opt_button in optional_button:
            opt_buttons.append(InlineKeyboardButton(
                text=LEXICON[opt_button] if opt_button in LEXICON else opt_button,
                callback_data=opt_button
            ))
        kb_builder.row(*opt_buttons, width=2)

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


def generate_cases_kb(cases: list, action: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    case_data = [(case['case_name'], case['id']) for case in cases]
    # Сценарий построения клавиатуры в случае запроса списка дел
    if action == 'get_case_list':
        for name, case_id in case_data:
            button = InlineKeyboardButton(text=name, callback_data=f'case_id_{case_id}')
            keyboard.inline_keyboard.append([button])

        keyboard.inline_keyboard.append([InlineKeyboardButton(text='📥 Добавить новое дело', callback_data='add_case')])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='back_menu')])

    # Сценарий построения клавиатуры в случае удаления дела
    elif action == 'confirm_delete_case':
        case_id = case_data[0][-1]
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=LEXICON['yes_delete'], callback_data='yes_delete')])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=LEXICON['no_cancel'],
                                                              callback_data=f'case_id_{case_id}')])

    return keyboard


def generate_chosen_case_kb(width: int,
                     *args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:

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

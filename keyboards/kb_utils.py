from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON


# Функция формирования инлайн клавиатуры
def create_inline_kb(width: int,
                     *args: str,
                     session_buttons: list | None = None,
                     note_buttons: list | None = None,
                     **kwargs: str) -> InlineKeyboardMarkup:

    # Инициализация билдера инлайн клавиатуры
    kb_builder = InlineKeyboardBuilder()
    # Список для кнопок

    if session_buttons:
        ses_buttons: list[InlineKeyboardButton] = []
        for ses_button in session_buttons:
            ses_buttons.append(InlineKeyboardButton(
                text=LEXICON[ses_button] if ses_button in LEXICON else ses_button,
                callback_data=ses_button
            ))
        kb_builder.row(*ses_buttons, width=2)

    if note_buttons:
        case_note_buttons: list[InlineKeyboardButton] = []
        for note_button in note_buttons:
            case_note_buttons.append(InlineKeyboardButton(
                text=LEXICON[note_button] if note_button in LEXICON else note_button,
                callback_data=note_button
            ))
        kb_builder.row(*case_note_buttons, width=2)

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

'''Переделать, разделить'''
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



def update_case_kb(*args, case_id: int) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    for button in args:
        buttons.append(InlineKeyboardButton(
            text=LEXICON[button] if button in LEXICON else button,
            callback_data=button))

    kb_builder.row(*buttons, width=2)
    back_button = InlineKeyboardButton(text=LEXICON['back'], callback_data=f'case_id_{case_id}')
    kb_builder.row(back_button, width=1)

    return kb_builder.as_markup()


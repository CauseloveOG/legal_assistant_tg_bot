from datetime import datetime

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.dao import get_user_cases, add_session_date_in_db
from handlers.session.reminders import toggle_notification
from keyboards.kb_utils import create_inline_kb
from lexicon.lexicon import LEXICON
from states.states import FSMChoiceCase
from utils.utils import get_sessions_text


session_handlers = Router()


# Добавление или обновление даты судебного заседания
@session_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data.in_({'add_s_d', 'update_s_d'}))
async def add_session_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMChoiceCase.add_court_session)
    await callback.message.edit_text(text=LEXICON['enter_court_session'])


# Обработка введенной даты судебного заседания
@session_handlers.message(StateFilter(FSMChoiceCase.add_court_session))
async def confirm_session_date(message: Message, state: FSMContext):
    try:
        date_time = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
        case_data = await state.get_data()
        await add_session_date_in_db(
            user_id=message.from_user.id,
            case_id=case_data['case']['id'],
            date=date_time
        )
    except ValueError:
        await message.reply("Неверный формат! Используй: ДД.ММ.ГГГГ ЧЧ:ММ")
    finally:
        await state.clear()
        case_kb = create_inline_kb(1, 'case', 'back_menu')
        await message.answer(text=LEXICON['confirm_add_session'],
                             reply_markup=case_kb)


# Функция отправки пользователю информации по всем датам судебных заседаний
@session_handlers.callback_query(F.data == 'court_sessions')
async def get_court_sessions(callback: CallbackQuery):
    cases = await get_user_cases(user_id=callback.from_user.id)
    sessions = await get_sessions_text(cases=cases)
    text = LEXICON['found_sessions'] + sessions if sessions else LEXICON['empty_sessions']
    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_kb(1, 'back_menu'))


# Меню настройки уведомлений
@session_handlers.callback_query(F.data.in_({'setting_notifications', 'turn_on', 'turn_off'}))
async def process_setting_notifications(callback: CallbackQuery):
    current_data = callback.data
    user_id = callback.from_user.id
    status_notification = await toggle_notification(user_id=user_id, status=current_data)

    if status_notification is None:
        await callback.message.edit_text(
            text=LEXICON['error'],
            reply_markup=create_inline_kb(1, 'back_menu'))
        return

    status_text = "включены ✔️" if status_notification else "выключены ❌"
    next_action = 'turn_off' if status_notification else 'turn_on'

    await callback.message.edit_text(text=LEXICON['notifications_menu'].format(status_text),
                                     reply_markup=create_inline_kb(1, next_action, 'back_menu'))

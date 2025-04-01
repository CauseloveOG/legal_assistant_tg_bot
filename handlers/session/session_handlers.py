from datetime import datetime

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.dao import get_user_cases, add_session_date_in_db, update_session_date_in_db, delete_session_from_db
from keyboards.kb_utils import create_inline_kb, update_case_kb, back_and_menu_kb
from lexicon.lexicon import LEXICON
from states.states import FSMChoiceCase
from utils.utils import get_sessions_text


session_handlers = Router()

# Меню взаимодействия с параметром "Судебное заседание"
@session_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'session_date')
async def process_session_date(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    case = user_data.get('case')
    case_id = case.get('id')
    available_session = case.get('session')
    session_buttons = ['update_s_d', 'delete_s_d'] if available_session else ['add_s_d']
    await callback.message.edit_reply_markup(
        reply_markup=update_case_kb(*session_buttons, case_id=case_id))


# Добавление даты судебного заседания
@session_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'add_s_d', )
async def add_session_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMChoiceCase.communicate_court_session)
    await state.update_data(state_session=callback.data)
    await callback.message.edit_text(text=LEXICON['enter_court_session'])

# Обновление даты судебного заседания
@session_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'update_s_d')
async def update_session_date(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    case = user_data.get('case')
    current_date = case.get('session').get('date').strftime('%d.%m.%Y %H:%M')
    await state.set_state(FSMChoiceCase.communicate_court_session)
    await state.update_data(state_session=callback.data)
    await callback.message.edit_text(text=LEXICON['update_court_session'].format(session_date=current_date))

# Удаление даты судебного заседания
@session_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'delete_s_d')
async def delete_session_date(callback: CallbackQuery, state: FSMContext):
    case_data = await state.get_data()
    case = case_data.get('case')
    case_id = case.get('id')
    await delete_session_from_db(user_id=callback.from_user.id, case_id=case_id)
    await state.set_state(FSMChoiceCase.case)
    case_kb = back_and_menu_kb(case_id=case_id)
    await callback.message.edit_text(text=LEXICON['confirm_delete_session'],
                         reply_markup=case_kb)

# Обработка введенной даты судебного заседания
@session_handlers.message(StateFilter(FSMChoiceCase.communicate_court_session))
async def confirm_add_session_date(message: Message, state: FSMContext):
    try:
        date_time = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
        case_data = await state.get_data()
        case = case_data.get('case')
        case_id = case.get('id')
        if case_data.get('state_session') == 'add_s_d':
            await add_session_date_in_db(
                user_id=message.from_user.id,
                case_id=case_id,
                date=date_time
            )
        elif case_data.get('state_session') == 'update_s_d':
            await update_session_date_in_db(
                user_id=message.from_user.id,
                case_id=case_id,
                date=date_time
            )
        await state.set_state(FSMChoiceCase.case)
        case_kb = back_and_menu_kb(case_id=case_id)
        await message.answer(text=LEXICON['confirm_add_session'],
                             reply_markup=case_kb)
    except ValueError:
        await message.reply("Неверный формат! Используй: ДД.ММ.ГГГГ ЧЧ:ММ")


# Функция отправки пользователю информации по всем датам судебных заседаний
@session_handlers.callback_query(F.data == 'court_sessions')
async def get_court_sessions(callback: CallbackQuery):
    cases = await get_user_cases(user_id=callback.from_user.id)
    sessions = await get_sessions_text(cases=cases)
    text = LEXICON['found_sessions'] + sessions if sessions else LEXICON['empty_sessions']
    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_kb(1, 'back_menu'))

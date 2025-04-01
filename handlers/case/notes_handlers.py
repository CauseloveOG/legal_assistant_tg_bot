from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.dao import add_note_in_db, delete_note_from_db
from keyboards.kb_utils import update_case_kb, back_and_menu_kb
from lexicon.lexicon import LEXICON
from states.states import FSMChoiceCase


notes_handlers = Router()

# Меню заметок с выбором действия
@notes_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'case_note')
async def process_session_date(callback: CallbackQuery, state: FSMContext):
    case_data = await state.get_data()
    case = case_data.get('case')
    case_id = case.get('id')
    note_buttons = ['update_note', 'delete_note'] if case.get('case_note') else ['add_note']
    await callback.message.edit_reply_markup(reply_markup=update_case_kb(*note_buttons, case_id=case_id))


# Добавление заметки к делу
@notes_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'add_note')
async def add_note_to_case(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMChoiceCase.case_note)
    await callback.message.edit_text(text='Напишите заметку: ')


# Обновление заметки по делу
@notes_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'update_note')
async def update_note_to_case(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMChoiceCase.case_note)
    case_data = await state.get_data()
    case = case_data.get('case')
    case_note = case.get('case_note')
    await callback.message.edit_text(text=LEXICON['note_info'].format(case_note=case_note))


# Подтверждение записи заметки к делу
@notes_handlers.message(StateFilter(FSMChoiceCase.case_note))
async def get_new_value(message: Message, state: FSMContext):
    case_data = await state.get_data()
    case = case_data.get('case')
    case_name = case.get('case_name')
    case_id = case.get('id')
    case_kb = back_and_menu_kb(case_id=case_id)
    await state.set_state(FSMChoiceCase.case)
    await add_note_in_db(case_id=case_id, note=message.text)
    await message.answer(text=LEXICON['confirm_case_note'].format(case_name=case_name), reply_markup=case_kb)


# Удаление заметки из БД
@notes_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'delete_note')
async def delete_note_from_case(callback: CallbackQuery, state: FSMContext):
    case_data = await state.get_data()
    case = case_data.get('case')
    case_id = case.get('id')
    case_kb = back_and_menu_kb(case_id=case_id)
    await delete_note_from_db(case_id=case_id)
    await state.set_state(FSMChoiceCase.case)
    await callback.message.edit_text(text=LEXICON['confirm_delete_note'],
                                     reply_markup=case_kb)
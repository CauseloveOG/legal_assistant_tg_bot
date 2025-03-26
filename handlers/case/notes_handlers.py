from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.dao import add_note_in_db, delete_note_from_db
from keyboards.kb_utils import create_inline_kb, update_case_kb
from lexicon.lexicon import LEXICON
from states.states import FSMChoiceCase


notes_handlers = Router()


@notes_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'case_note')
async def process_session_date(callback: CallbackQuery, state: FSMContext):
    case = await state.get_data()
    case_id = case['case']['id']
    note_buttons = ['update_note', 'delete_note'] if case['case']['case_note'] else ['add_note']
    await callback.message.edit_text(text='Здесь вы можете Добавить, Обновить или удалить заметку:',
                                     reply_markup=update_case_kb(*note_buttons, case_id=case_id))


# Добавление или изменение заметки к делу
@notes_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data.in_({'add_note', 'update_note'}))
async def add_note_to_case(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMChoiceCase.add_note)
    await callback.message.edit_text(text='Напишите заметку: ')


# Подтверждение добавления заметки к делу
@notes_handlers.message(StateFilter(FSMChoiceCase.add_note))
async def get_new_value(message: Message, state: FSMContext):
    case_data = await state.get_data()
    await state.clear()
    await add_note_in_db(case_id=case_data['case']['id'], note=message.text)
    await message.answer(text=f'Заметка для дела {case_data['case']["case_name"]} успешно добавлена.',
                         reply_markup=create_inline_kb(1, 'case'))


# Удаление заметки из БД
@notes_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'delete_note')
async def delete_note_from_case(callback: CallbackQuery, state: FSMContext):
    case_data = await state.get_data()
    await state.clear()
    await delete_note_from_db(case_id=case_data['case']['id'])
    await callback.message.edit_text(text='Заметка удалена',
                                     reply_markup=create_inline_kb(1, 'case'))
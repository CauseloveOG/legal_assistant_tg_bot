from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.dao import edit_case
from keyboards.kb_utils import update_case_kb, back_and_menu_kb, delete_case_kb
from lexicon.lexicon import LEXICON
from states.states import FSMChoiceCase


upd_case_handlers = Router()


# Меню для выбора какой параметр необходимо отредактировать
@upd_case_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'edit_case')
async def start_edit_case(callback: CallbackQuery, state: FSMContext):
    case_data = await state.get_data()
    case = case_data.get('case')
    case_id = case.get('id')
    buttons = ['ed_case_name', 'ed_case_number', 'ed_court_name', 'delete_case']
    case_kb = update_case_kb(*buttons, case_id=case_id)
    await callback.message.edit_reply_markup(reply_markup=case_kb)


# Запрос нового значения для редактирования выбранного параметра
@upd_case_handlers.callback_query(F.data.startswith('ed_'))
async def enter_new_value(callback: CallbackQuery, state: FSMContext):
    await state.update_data(column=callback.data.replace('ed_', ''))
    await state.set_state(FSMChoiceCase.edit_case)
    await callback.message.edit_text(text='Введите новое значение: ')


# Подтверждение редактирования выбранного параметра
@upd_case_handlers.message(StateFilter(FSMChoiceCase.edit_case))
async def get_new_value(message: Message, state: FSMContext):
    user_data = await state.get_data()
    column = user_data.get('column')
    case = user_data.get('case')
    case_name = case.get('case_name')
    case_id = case.get('id')
    case_kb = back_and_menu_kb(case_id=case_id)
    await state.set_state(FSMChoiceCase.case)
    await edit_case(case_id=case_id, column=column, new_value=message.text)
    await message.answer(text=LEXICON['edit_case_confirm'].format(case_name=case_name),
                         reply_markup=case_kb)


# Удаление выбранного дела пользователя
@upd_case_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'delete_case')
async def delete_case_process(callback: CallbackQuery, state: FSMContext):
    case_data = await state.get_data()
    case = case_data.get('case')
    case_id = case.get('id')
    case_name = case.get('case_name')
    case_kb = delete_case_kb(case_id=case_id)
    await callback.message.edit_text(text=LEXICON['confirm_delete'].format(case_name),
                                     reply_markup=case_kb)

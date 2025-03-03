from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.dao import edit_case
from keyboards.kb_utils import create_inline_kb, generate_cases_kb
from lexicon.lexicon import LEXICON
from states.states import FSMChoiceCase


upd_case_handlers = Router()

# Меню для выбора какой параметр необходимо отредактировать
@upd_case_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'edit_case')
async def start_edit_case(callback: CallbackQuery):
    edit_kb = create_inline_kb(1, 'ed_case_name', 'ed_case_number', 'ed_court_name',
                               'case')
    await callback.message.edit_text(text=LEXICON['choice_edit_case'],
                                     reply_markup=edit_kb)

# Запрос нового значения от пользователя
@upd_case_handlers.callback_query(F.data.startswith('ed_'))
async def enter_new_value(callback: CallbackQuery, state: FSMContext):
    await state.update_data(column=callback.data.replace('ed_', ''))
    await state.set_state(FSMChoiceCase.edit_case)
    await callback.message.edit_text(text='Введите новое значение: ')

# Подтверждение редактирования выбранного параметра
@upd_case_handlers.message(StateFilter(FSMChoiceCase.edit_case))
async def get_new_value(message: Message, state: FSMContext):
    case_data = await state.get_data()
    await state.clear()
    await edit_case(case_id=case_data['case']['id'], column=case_data['column'], new_value=message.text)
    await message.answer(text=f'Дело с названием {case_data['case']["case_name"]} успешно отредактировано.',
                         reply_markup=create_inline_kb(1, 'case'))


# Удаление выбранного дела пользователя
@upd_case_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'delete_case')
async def delete_case_process(callback: CallbackQuery, state: FSMContext):
    case_data = await state.get_data()
    kb = generate_cases_kb([case_data['case']], action='confirm_delete_case')
    await callback.message.edit_text(text=LEXICON['confirm_delete'].format(case_data['case']['case_name']),
                                     reply_markup=kb)
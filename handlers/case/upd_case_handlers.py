from datetime import datetime

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.dao import edit_case, add_session_date_in_db
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


# Добавление даты судебного заседания
@upd_case_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'add_session_date')
async def add_session_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMChoiceCase.add_court_session)
    await callback.message.edit_text(text=LEXICON['enter_court_session'])


# Обработка введенной даты судебного заседания
@upd_case_handlers.message(StateFilter(FSMChoiceCase.add_court_session))
async def confirm_session_date(message: Message, state: FSMContext):
    try:
        date_time = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
        case_data = await state.get_data()
        await add_session_date_in_db(case_id=case_data['case']['id'], date=date_time)
    except ValueError:
        await message.reply("Неверный формат! Используй: ДД.ММ.ГГГГ ЧЧ:ММ")
    finally:
        await state.clear()
    case_kb = create_inline_kb(1, 'case', 'back_menu')
    await message.answer(text='Дата добавлена',
                         reply_markup=case_kb)
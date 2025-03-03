from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.dao import get_user_cases, delete_case_by_id
from keyboards.kb_utils import generate_cases_kb, create_inline_kb
from lexicon.lexicon import LEXICON
from states.states import FSMChoiceCase


case_handlers = Router()

# Вкладка Мои дела
# Выводит перечень всех дел в виде инлайн клавиатур
@case_handlers.callback_query(F.data.in_({'case', 'yes_delete', 'cancel_added'}))
async def process_case_button(callback: CallbackQuery, state: FSMContext):
    # Вывод дел в случае удаления дела
    if callback.data == 'yes_delete':
        case_data =  await state.get_data()
        await delete_case_by_id(case_id=case_data['case']['id'])
        await callback.answer(text=LEXICON['delete_confirmation'].format(case_name=case_data['case']['case_name']))

    await state.clear()

    cases = await get_user_cases(user_id=callback.from_user.id) # Получение списка дел
    await state.set_state(FSMChoiceCase.case)
    await state.update_data(cases_list=cases)
    await callback.message.edit_text(text=LEXICON['not_empty_cases'] if cases else LEXICON['empty_cases'],
                                     reply_markup=generate_cases_kb(cases=cases, action='get_case_list'))


# Получение информации по выбранному делу
@case_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data.startswith('case_id_'))
async def get_chosen_case(callback: CallbackQuery, state: FSMContext):
    cases = await state.get_data()
    case_id = int(callback.data.replace('case_id_', ''))
    case = [case for case in cases['cases_list'] if case['id'] == case_id]
    case_info = LEXICON['chosen_user_case'].format(case_name=case[0]['case_name'],
                                                   court_name=case[0]['court_name'],
                                                   case_number=case[0]['case_number'])
    case_kb = create_inline_kb(1, 'add_session_date', 'edit_case',
                               'delete_case', 'case', 'back_menu')
    await state.update_data(case=case[0]) # получаем словарь данных выбранного дела
    await callback.message.edit_text(text=case_info,
                                     reply_markup=case_kb)

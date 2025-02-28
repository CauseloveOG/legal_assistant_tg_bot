from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.dao import get_user_cases
from keyboards.kb_utils import generate_cases_kb, create_inline_kb
from lexicon.lexicon import LEXICON
from states.states import FSMChoiceCase


case_handlers = Router()

# Вкладка Мои дела
# Выводит перечень всех дел в виде инлайн клавиатур
@case_handlers.callback_query(F.data.in_({'case', 'yes_delete', 'cancel_added'}))
async def process_case_button(callback: CallbackQuery, state: FSMContext):
    # Вывод дел в случае удаления дела
    # if callback.data == 'yes_delete':
    #     case_name =  await state.get_data()
    #     await callback.answer(text=await delete_case_from_list(callback.from_user.id, case_name['case_name']))
    #     await state.clear()
    await state.clear()
    cases = await get_user_cases(user_id=callback.from_user.id) # Получение списка дел
    if cases:
        text = LEXICON['not_empty_cases']
        case_names = [case['case_name'] for case in cases]
        await state.update_data(case_names=case_names)
        await state.set_state(FSMChoiceCase.choice_case)
    else:
        text = LEXICON['empty_cases']
    await callback.message.edit_text(text=text,
                                     reply_markup=generate_cases_kb(cases=cases))

# Получение информации по выбранному делу
@case_handlers.callback_query(StateFilter(FSMChoiceCase.choice_case), F.data.startswith('case_id_'))
async def get_chosen_case(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMChoiceCase.case)
    cases = await get_user_cases(user_id=callback.from_user.id)
    case_id = int(callback.data.replace('case_id_', ''))
    case = [case for case in cases if case['id'] == case_id]
    case_info = LEXICON['chosen_user_case'].format(case_name=case[0]['case_name'],
                                                   court_name=case[0]['court_name'],
                                                   case_number=case[0]['case_number'])
    case_kb = create_inline_kb(1, 'add_session_date', 'edit_case',
                               'delete_case', 'case', 'back_menu')
    await state.update_data(case_id=case_id, case_name=case[0]['case_name'])
    await callback.message.edit_text(text=case_info,
                                     reply_markup=case_kb)

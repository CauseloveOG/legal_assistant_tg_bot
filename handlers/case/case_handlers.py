import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.dao import get_user_cases, delete_case_by_id, get_user_chosen_case
from keyboards.kb_utils import generate_cases_kb, create_inline_kb
from lexicon.lexicon import LEXICON
from states.states import FSMChoiceCase
from utils.utils import format_case_info


case_handlers = Router()


# Вкладка Мои дела.
# Возвращает перечень всех дел в виде инлайн клавиатур
@case_handlers.callback_query(F.data.in_({'case', 'yes_delete', 'cancel_added'}))
async def process_case_button(callback: CallbackQuery, state: FSMContext):
    # Вывод дел в случае удаления дела
    if callback.data == 'yes_delete':
        case_data =  await state.get_data()
        case = case_data.get('case')
        case_id = case.get('id')
        case_name = case.get('case_name')
        await delete_case_by_id(case_id=case_id)
        await callback.answer(
            text=LEXICON['delete_confirmation'].format(case_name=case_name)
        )
    await state.clear()
    case_list = await get_user_cases(user_id=callback.from_user.id) # Получение списка дел
    await state.set_state(FSMChoiceCase.case)
    await state.update_data(cases_list=case_list)
    await callback.message.edit_text(
        text=LEXICON['not_empty_cases'] if case_list else LEXICON['empty_cases'],
        reply_markup=generate_cases_kb(cases=case_list)
    )


# Получение информации по выбранному делу
@case_handlers.callback_query(StateFilter(FSMChoiceCase.case),
                              F.data.startswith(('case_id_', 'back_case_id_')))
async def get_chosen_case(callback: CallbackQuery, state: FSMContext):
    kb_buttons = ['session_date', 'case_note', 'edit_case', 'case', 'back_menu']
    case_kb = create_inline_kb(1,*kb_buttons)
    user_id = callback.from_user.id
    if callback.data.startswith('back_case_id_'):
        await callback.message.edit_reply_markup(reply_markup=case_kb)
    else:
        case_id = int(callback.data.replace('case_id_', ''))
        case: dict | None = await get_user_chosen_case(case_id=case_id, user_id=user_id)
        if not case:
            await callback.message.edit_text(
                text=LEXICON['case_not_found'],
                reply_markup=create_inline_kb(1, 'back_menu')
            )
            return

        await state.update_data(case=case)
        # Форматирование в итоговый текс информации по выбранному делу
        case_info: str | None = format_case_info(case=case)
        logging.info(f'Отображено дело для пользователя {callback.from_user.id}')
        await callback.message.edit_text(text=case_info, reply_markup=case_kb)



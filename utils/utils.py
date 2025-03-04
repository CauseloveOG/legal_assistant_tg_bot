from aiogram.fsm.context import FSMContext

from lexicon.lexicon import LEXICON


# Функция для получения словаря данных запрошенного пользователем дела
async def get_case_from_state(state: FSMContext, case_id: int) -> dict:
    data = await state.get_data()
    return next((case for case in data['cases_list'] if case['id'] == case_id), None)


# Функция для формирования информации о деле с учетом добавления даты заседания
async def get_case_info(case: dict):
    res = LEXICON['chosen_user_case'].format(
        case_name=case['case_name'],
        court_name=case['court_name'],
        case_number=case['case_number'],
        session_date='')
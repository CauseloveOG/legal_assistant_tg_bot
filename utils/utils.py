import logging
from typing import List, Optional

from aiogram.fsm.context import FSMContext

from lexicon.lexicon import LEXICON


# Функция для получения словаря данных запрошенного пользователем дела
async def get_case_from_state(state: FSMContext, case_id: int) -> Optional[dict]:
    data = await state.get_data()
    return next((case for case in data['cases_list'] if case['id'] == case_id), None)


# Функция форматирования информации о деле и заседании в текст
def format_case_session(case: dict) -> str:
    return LEXICON['chosen_user_case'].format(
        case_name=case['case_name'],
        court_name=case['court_name'],
        case_number=case['case_number'],
        session_date=case['session']['date'].strftime('%d.%m.%Y %H:%M') if case['session'] else 'не указаны.'
    )

# Функция сортировки и применения форматирования информации по заседаниям всех дел
async def get_sessions_text(cases: List[dict]) -> Optional[str]:
    try:
        session_cases = [case for case in cases if case['session']]
        if not session_cases:
            return None

        sorted_cases = sorted(session_cases, key=lambda x: x['session']['date'])

        txt = [format_case_session(case) for case in sorted_cases]
        return '\n\n'.join(txt)

    except Exception as e:
        logging.error(f'Ошибка при форматировании списка заседаний: {e}')
        return None
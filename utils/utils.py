import logging
from typing import List, Optional

from aiogram.fsm.context import FSMContext
import httpx

from database.models import Case
from lexicon.lexicon import LEXICON


# Функция для получения словаря данных запрошенного пользователем дела
async def get_case_from_state(state: FSMContext, case_id: int) -> dict | None:
    data = await state.get_data()
    cases_list = data.get('cases_list')
    if cases_list:
        return next((case for case in cases_list if case['id'] == case_id), None)
    else:
        return None


# Функция форматирования информации о деле и заседании в текст
def format_case_info(case: dict) -> str:
    return LEXICON['chosen_user_case'].format(
        case_name=case.get('case_name'),
        court_name=case.get('court_name'),
        case_number=case.get('case_number'),
        session_date=case.get('session').get('date').strftime('%d.%m.%Y %H:%M') if case.get('session') else 'не указаны.',
        case_note=case.get('case_note') if case.get('case_note') else 'отсутствует.'
    )

def format_cases_sessions(case: dict) -> str:
    return LEXICON['info_for_sessions'].format(
        case_name=case['case_name'],
        court_name=case['court_name'],
        case_number=case['case_number'],
        session_date=case['session']['date'].strftime('%d.%m.%Y %H:%M')
    )

# Функция сортировки и применения форматирования информации по заседаниям всех дел
async def get_sessions_text(cases: List[dict]) -> Optional[str]:
    try:
        session_cases = [case for case in cases if case['session']]
        if not session_cases:
            return None

        sorted_cases = sorted(session_cases, key=lambda x: x['session']['date'])

        txt = [format_cases_sessions(case) for case in sorted_cases]
        return '\n\n'.join(txt)

    except Exception as e:
        logging.error(f'Ошибка при форматировании списка заседаний: {e}')
        return None

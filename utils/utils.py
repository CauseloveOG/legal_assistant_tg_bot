import logging
from datetime import timedelta
from typing import List, Optional

from aiogram.fsm.context import FSMContext
import httpx

from config_data.config import Config, load_config
from database.base import connection
from lexicon.lexicon import LEXICON
from database.models import User, Case, Session


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


"""Функции для для реализации работы с Google Calendar"""

config: Config = load_config()

# Генерация URL для авторизации
async def get_auth_url(user_id: int) -> str:
    auth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth?'
        f'client_id={config.bot.client_id}&'
        'redirect_uri=urn:ietf:wg:oauth:2.0:oob&'
        'response_type=code&'
        'scope=https://www.googleapis.com/auth/calendar.events&'
        f'state={user_id}&access_type=offline&prompt=consent'
    )
    return auth_url

# Обмен кода на токены
async def exchange_code_for_tokens(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": config.bot.client_id,
                "client_secret": config.bot.client_secret,
                "redirect_uri": config.bot.redirect_uri,
                "grant_type": "authorization_code",
            }
        )
        return response.json()


# Обновление токена пользователя
@connection
async def refresh_access_token(session, user: User) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": config.bot.client_id,
                "client_secret": config.bot.client_secret,
                "refresh_token": user.refresh_token,
                "grant_type": "refresh_token",
            }
        )
        tokens = response.json()
        user.access_token = tokens['access_token']
        await session.commit()
        return tokens['access_token']


# Добавление события в Гугл календарь
async def add_to_google_calendar(user: User, session: Session, case: Case) -> str | None:
    if not user.access_token:
        return None
    headers = {'Authorization': f'Bearer {user.access_token}'}
    event = {
        'summary': f'Заседание: {case.case_name}',
        'location': case.court_name,
        'start': {
            'dateTime': session.date.isoformat(),
            'timeZone': 'UTC'
        },
        'end': {
            'dateTime': (session.date + timedelta(hours=1)).isoformat(),
            'timeZone': 'UTC'
        },
    }
    async with httpx.AsyncClient() as client:
        try:
            # Первый запрос
            response = await client.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers=headers,
                json=event
            )
            # В случае, если токен пользователя истек
            if response.status_code == 401:
                access_token = await refresh_access_token(user)
                headers['Authorization'] = f'Bearer {access_token}'
                # Второй запрос с новым токеном
                response = await client.post(
                    "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                    headers=headers,
                    json=event
                )

            # Проверка статуса ответа
            if response.status_code != 200:
                logging.error(f'Ошибка Google Calendar API: {response.status_code}, ответ: {response.text}')
                return None
            event_data = response.json()
            event_id = event_data.get('id')
            if not event_id:
                logging.error(f'Не удалось получить event_id из ответа: {event_data}')

            logging.info(f'Событие успешно добавлено в Google Calendar: event_id={event_id}')
            return event_id
        except Exception as e:
            logging.error(f'Ошибка добавления в Google calendar: {e}')
            return None


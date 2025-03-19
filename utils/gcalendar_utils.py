import logging
from datetime import timedelta

import httpx
from config_data.config import Config, load_config
from database.base import connection
from database.models import User, Session, Case


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
async def add_to_google_calendar(user: User, case: Case, date) -> str | None:
    if not user.access_token:
        return None

    headers = {'Authorization': f'Bearer {user.access_token}'}
    event = {
        'summary': f'Заседание по делу: {case.case_name}\n'
                   f'Номер дела: {case.case_number}',
        'location': case.court_name,
        'start': {
            'dateTime': date.isoformat(),
            'timeZone': 'Europe/Moscow'
        },
        'end': {
            'dateTime': (date + timedelta(hours=1)).isoformat(),
            'timeZone': 'Europe/Moscow'
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


# Обновление события в календаре
async def update_google_event(user: User, case: Case, session: Session, date) -> str | None:
    if not user.access_token:
        return None

    if session.google_event_id is None:
        return await add_to_google_calendar(user=user, case=case, date=date)
    else:
        headers = {'Authorization': f'Bearer {user.access_token}'}
        event = {
            'summary': f'Заседание по делу: {case.case_name}\n'
                       f'Номер дела: {case.case_number}',
            'location': case.court_name,
            'start': {
                'dateTime': date.isoformat(),
                'timeZone': 'Europe/Moscow'
            },
            'end': {
                'dateTime': (date + timedelta(hours=1)).isoformat(),
                'timeZone': 'Europe/Moscow'
            }
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{session.google_event_id}',
                    headers=headers,
                    json=event
                )
                if response.status_code == 401:
                    access_token = await refresh_access_token(user)
                    headers['Authorization'] = f'Bearer {access_token}'
                    response = await client.patch(
                        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                        headers=headers,
                        json=event
                    )

                if response.status_code != 200:
                    logging.error(f'Ошибка Google Calendar API: {response.status_code}, ответ: {response.text}')
                    return None
            logging.info(f'Событие с ID {session.google_event_id} успешно обновлено в Google calendar.')
        except Exception as e:
            logging.error(f'Ошибка при обновлении события в Google calendar: {e}')


# Удаление события из G-calendar
async def delete_google_event(user: User, google_event_id: str):
    if not user.access_token or not google_event_id:
        return
    headers = {'Authorization': f'Bearer {user.access_token}'}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{google_event_id}",
                headers=headers
            )
            if response.status_code == 401:
                access_token = await refresh_access_token(user)
                headers['Authorization'] = f'Bearer {access_token}'
                await client.delete(
                    f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{google_event_id}",
                    headers=headers
                )
            logging.info(f'Событие с ID {google_event_id} успешно удалено из Google calendar.')
    except Exception as e:
        logging.error(f'Ошибка при удалении события из Google calendar:{e}')
import logging

from sqlalchemy import select
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from utils.gcalendar_utils import add_to_google_calendar, update_google_event, delete_google_event
from .base import connection
from .models import User, Case, Session


# Проверяет есть ли пользователь в таблице users.
# Если нет, то добавляет пользователя БД
@connection
async def set_user(session, tg_id: int, username: str, full_name: str) -> Optional[User]:
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))
        if not user:
            new_user = User(id=tg_id, username=username, full_name=full_name)
            session.add(new_user)
            await session.commit()
            logging.info(f'Пользователь с ID {tg_id} добавлен в БД.')
        else:
            logging.info(f'Пользователь с ID {tg_id} найден!')
    except SQLAlchemyError as e:
        logging.info(f'Ошибка при добавлении пользователя {e}')
        await session.rollback()


@connection
async def get_user_info(session, user_id: int) -> User | None:
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))
        return user
    except Exception as e:
        logging.error(f'Ошибка при получении информации о пользователе: {e}')
        return None


# Получение всех дел пользователя
@connection
async def get_user_cases(session, user_id: int) -> List[Dict[str, Any]]:
    try:
        result = await session.execute(
            select(Case)
            .filter_by(user_id=user_id)
            .options(joinedload(Case.session))
        )

        cases = result.scalars().all()
        if not cases:
            logging.info(f'Дела пользователя с ID {user_id} не найдены.')
            return []

        cases_list = [
            {
                'id': case.id,
                'case_name': case.case_name,
                'case_number': case.case_number,
                'court_name': case.court_name,
                'session': {
                    'date': case.session.date
                } if case.session else None,
                'case_note': case.case_note
            }
            for case in cases
        ]
        logging.info(f'Получена информация по всем делам пользователя с ID {user_id}')
        return cases_list
    except SQLAlchemyError as e:
        logging.error(f'Ошибка при получении дел: {e}')
        return []


# Метод добавления дела в БД
@connection
async def add_case(session, user_id: int, case_name: str, case_number: str, court_name: str) -> Case | None:
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))
        if not user:
            logging.error(f'Пользователь с ID {user_id} не найден.')
            return None
        new_case = Case(
            user_id=user_id,
            case_name=case_name,
            case_number=case_number,
            court_name=court_name
        )
        session.add(new_case)
        await session.commit()
        logging.info(f'Дело пользователя с ID {user_id} успешно добавлено.')
        return new_case
    except SQLAlchemyError as e:
        logging.error(f'Ошибка при добавлении дела: {e}')
        await session.rollback()


# Метод радактирования дела в БД
@connection
async def edit_case(session, case_id: int, column: str, new_value: str) -> Case | None:
    try:
        case = await session.scalar(select(Case).filter_by(id=case_id))
        if not case:
            logging.error(f'Дело с ID {case_id} не найдено.')
            return None

        match column:
            case 'case_name': case.case_name = new_value
            case 'case_number': case.case_number = new_value
            case 'court_name': case.court_name = new_value
        await session.commit()
        logging.info(f'Дело с ID {case_id} успешно обновлено.')
        return case
    except SQLAlchemyError as e:
        logging.error(f'Ошибка при обновлении дела: {e}')
        await session.rollback()

# Добавление или обновление заметки в БД
@connection
async def add_note_in_db(session, case_id: int, note: str) -> None:
    try:
        case = await session.scalar(select(Case).filter_by(id=case_id))
        if not case:
            logging.error(f'Дело с ID {case_id} не найдено.')
            return None
        case.case_note = note
        await session.commit()
        logging.info(f'Заметка для дела с ID {case_id} успешно добавлена.')
    except SQLAlchemyError as e:
        logging.error(f'Ошибка при добавлении заметки: {e}')
        await session.rollback()

# Удаление заметки из БД
@connection
async def delete_note_from_db(session, case_id: int) -> None:
    try:
        case = await session.scalar(select(Case).filter_by(id=case_id))
        if not case:
            logging.error(f'Дело с ID {case_id} не найдено.')
            return None
        case.case_note = None
        await session.commit()
        logging.info(f'Заметка для дела с ID {case_id} успешно удалена.')
    except SQLAlchemyError as e:
        logging.error(f'Ошибка при удалении заметки: {e}')



# Метод удаления дела из БД
@connection
async def delete_case_by_id(session, case_id: int) -> None:
    try:
        case = await session.get(Case, case_id)
        if not case:
            logging.error(f'Дело с ID {case_id} не найдено.')
        await session.delete(case)
        await session.commit()
        logging.info(f'Дело с ID {case_id} успешно удалено.')
    except SQLAlchemyError as e:
        logging.error(f'Ошибка при удалении дела: {e}')


# Добавление даты заседания в БД
@connection
async def add_session_date_in_db(session, user_id: int, case_id: int, date) -> None:
    try:
        user = await session.scalar(
            select(User).filter_by(id=user_id)
        )
        case = await session.scalar(
            select(Case).filter_by(id=case_id)
        )

        new_session = Session(
            case_id=case_id,
            date=date
        )

        session.add(new_session)
        await session.commit()
        if user.access_token:
            google_event_id = await add_to_google_calendar(user=user, case=case, date=date)
            if google_event_id:
                new_session.google_event_id = google_event_id
                await session.commit()
                logging.info(f"Событие добавлено в Google Calendar: event_id={google_event_id}")
        logging.info(f'Дата судебного заседания по делу с ID {case_id} успешно добавлена.')
    except SQLAlchemyError as e:
        logging.error(f'Ошибка при добавлении даты: {e}')
        await session.rollback()
        return None


# Метод обновления даты заседания в БД и G-calendar
@connection
async def update_session_date_in_db(session, user_id: int, case_id: int, date):
    try:
        user = await session.scalar(
            select(User).filter_by(id=user_id)
        )
        existing_session = await session.scalar(
            select(Session).filter_by(case_id=case_id)
        )
        case = await session.scalar(
            select(Case).filter_by(id=case_id)
        )
        existing_session.date = date
        existing_session.reminder_sent = False
        await session.commit()
        if user.access_token:
            google_event_id = await update_google_event(user=user, session=existing_session, case=case, date=date)
            if google_event_id:
                existing_session.google_event_id = google_event_id
                await session.commit()
        logging.info(f'Дата заседания для дела с ID {case_id} успешно обновлена.')
    except SQLAlchemyError as e:
        logging.error(f'Ошибка при добавлении даты: {e}')
        await session.rollback()
        return None

# Удаление даты заседания из БД
@connection
async def delete_session_from_db(session, user_id: int, case_id: int):
    try:
        user = await session.get(User, user_id)
        existing_session = await session.scalar(
            select(Session).filter_by(case_id=case_id)
        )
        if not existing_session:
            logging.error(f'Заседания для дела с ID {case_id} не найдено.')
        if existing_session.google_event_id:
            await delete_google_event(user=user, google_event_id=existing_session.google_event_id)
        await session.delete(existing_session)
        await session.commit()
        logging.info(f'Сведения о заседании по делу с ID {case_id} успешно удалено.')

    except SQLAlchemyError as e:
        logging.error(f'Ошибка при удалении сведений о заседании: {e}')


# Сохранение токена пользователя
@connection
async def save_tokens(session, user_id: int, tokens: dict):
    try:
        stmt = select(User).filter_by(id=user_id)
        result = await session.execute(stmt)
        user = result.scalars().one_or_none()
        if user:
            user.access_token = tokens['access_token']
            user.refresh_token = tokens.get('refresh_token')
            await session.commit()
            logging.info(f"Токены сохранены для user_id={user_id}")
    except Exception as e:
        logging.error(f'Ошибка при сохранении токена: {e}')


@connection
async def toggle_google_sync(session, user_id: int, status: str) -> bool | None:
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))

        if not user:
            logging.error(f"Пользователь с ID {user_id} не найден.")
            return None

        match status:
            case 'enable_gcalendar_sync':
                user.google_sync_enabled = True
                logging.info(f"Синхронизация с Google Calendar включена для user_id={user_id}")
            case 'disable_gcalendar_sync':
                user.google_sync_enabled = False
                logging.info(f"Синхронизация с Google Calendar отключена для user_id={user_id}")
        await session.commit()

        return user.google_sync_enabled
    except Exception as e:
        logging.error(f'Ошибка при переключении синхронизации: {e}')


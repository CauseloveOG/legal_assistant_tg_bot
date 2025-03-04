import logging

from sqlalchemy import select
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

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

# Получение списка дел. Возвращает список словарей или пустой список
# @connection
# async def get_user_cases(session, user_id: int) -> List[Dict[str, Any]]:
#     try:
#         cases = await session.execute(select(Case).filter_by(user_id=user_id))
#         cases = cases.scalars().all()
#         if not cases:
#             logging.info(f'Дела пользователя с ID {user_id} не найдены.')
#             return []
#
#         # Сделать проверку через лог, в каком виде получаем данные
#         cases_list = [
#             {
#                 'id': case.id,
#                 'case_name': case.case_name,
#                 'case_number': case.case_number,
#                 'court_name': case.court_name
#             } for case in cases
#         ]
#         return cases_list
#     except SQLAlchemyError as e:
#         logging.error(f'Ошибка при получении дел: {e}')
#         return []

'''Доделать запрос'''
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

        # Сделать проверку через лог, в каком виде получаем данные
        cases_list = [
            {
                'id': case.id,
                'case_name': case.case_name,
                'case_number': case.case_number,
                'court_name': case.court_name,
                'session': case.session.date.strftime('%d.%m.%Y %H:%M') if case.session else None
            }
            for case in cases
        ]
        logging.info(f'Получены данные дела для пользователя {user_id}')
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
async def add_session_date_in_db(session, case_id: int, date):
    try:
        existing_session = await session.scalar(select(Session).filter_by(case_id=case_id))

        if existing_session:
            existing_session.date = date
            await session.commit()
            logging.info(f'Дата заседания для дела с ID {case_id} успешно обновлена.')
        else:
            new_session = Session(
                case_id=case_id,
                date=date
            )
            session.add(new_session)
            await session.commit()
            logging.info(f'Дата судебного заседания по делу с ID {case_id} успешно добавлено.')
            return new_session

    except SQLAlchemyError as e:
        logging.error(f'Ошибка при добавлении даты: {e}')
        await session.rollback()
        return None

'''
Добавить проверку на наличие даты заседания с ID дела.
Если заседание для такого дела есть, то внести изменения в старую запись.
Если нет, то создать новое.
Хранить в БД только дату последнего заседания.

Обдумать вариант добавления дела в архив, после его завершения.
'''
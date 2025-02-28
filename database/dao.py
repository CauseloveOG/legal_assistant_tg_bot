import logging

from sqlalchemy import select
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError

from .base import connection
from .models import User, Case


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
async def get_user_cases(session, user_id: int) -> List[Dict[str, Any]]:
    try:
        cases = await session.execute(select(Case).filter_by(user_id=user_id))
        cases = cases.scalars().all()
        if not cases:
            logging.info(f'Дела пользователя с ID {user_id} не найдены.')
            return []

        # Сделать проверку через лог, в каком виде получаем данные
        cases_list = [
            {
                'id': case.id,
                'case_name': case.case_name,
                'case_number': case.case_number,
                'court_name': case.court_name
            } for case in cases
        ]
        return cases_list
    except SQLAlchemyError as e:
        logging.error(f'Ошибка при получении дел: {e}')
        return []


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

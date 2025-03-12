from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from sqlalchemy import select
from datetime import datetime, timedelta
import logging
from aiogram import Bot
from sqlalchemy.orm import joinedload

from database.base import connection
from database.models import Session, Case, User


# Проверка уведомлений для отправки
@connection
async def check_reminder(session, bot: Bot) -> None:
    """Проверка предстоящих заседаний и отправка напоминаний"""
    try:
        current_time = datetime.now()
        stmt = (
            select(User)
            .filter_by(reminder_enabled=True)
            .options(joinedload(User.cases).joinedload(Case.session))
            )
        result = await session.execute(stmt)
        users = result.unique().scalars().all()

        if not users:
            logging.info(f'Пользователей с активными уведомлениями не найдено.')
        elif users:
            logging.info(f'Количество пользователей с активными уведомлениями: {len(users)}')

        for user in users:
            for case in user.cases:
                if case.session and case.session.date and case.session.reminder_sent is not True:
                    reminder_time = case.session.date - timedelta(days=1)
                    if reminder_time <= current_time < case.session.date:
                        message = (
                            f"Напоминание: Завтра, {case.session.date.strftime('%d.%m.%Y %H:%M')}, "
                            f"состоится заседание по делу '{case.case_name}' в {case.court_name}."
                        )
                        try:
                            await bot.send_message(chat_id=user.id, text=message)
                            case.session.reminder_sent = True
                            await session.commit()
                            logging.info(f"Напоминание отправлено: user_id={user.id}, case_id={case.id}")
                        except Exception as e:
                            logging.error(f'Ошибка отправки уведомления пользователю {user.id}: {e}')
    except Exception as e:
        logging.error(f'Ошибка в check_reminders: {e}')


# Переключение состояния уведомлений
@connection
async def toggle_notification(session, user_id: int, status: str) -> Optional[bool]:
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))

        if not user:
            logging.info(f'Пользователь с ID {user_id} не найден.')
            return None

        match status:
            case 'turn_on':
                user.reminder_enabled = True
            case 'turn_off':
                user.reminder_enabled = False
        await session.commit()

        return user.reminder_enabled
    except Exception as e:
        logging.error(f'Ошибка при переключении режима уведомлений: {e}')
        return None


async def start_reminder_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(event_loop=asyncio.get_running_loop())
    scheduler.add_job(check_reminder, 'interval', minutes=15, args=(bot,))
    scheduler.start()
    logging.info('Планировщик запущен')

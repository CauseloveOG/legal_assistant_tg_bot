import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import load_config, Config
from database.base import create_tables
from handlers.case.add_case_handlers import add_case_handlers
from handlers.case.case_handlers import case_handlers
from handlers.case.upd_case_handlers import upd_case_handlers
from handlers.start_handlers import start_handlers
from keyboards.main_menu import set_main_menu


logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logging.info('Starting bot')

    config: Config = load_config()

    storage = MemoryStorage()

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    # # Создание БД
    await create_tables()

    # Главное меню
    await set_main_menu(bot)

    # Роутеры
    dp.include_router(start_handlers)
    dp.include_router(case_handlers)
    dp.include_router(add_case_handlers)
    dp.include_router(upd_case_handlers)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())
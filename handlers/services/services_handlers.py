from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.kb_utils import create_inline_kb

services_handlers = Router()

# Меню сервисов
@services_handlers.callback_query(F.data == 'services')
async def process_start_button(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    main_menu_kb = create_inline_kb(1, 'g_calendar', 'setting_notifications', 'back_menu')
    await callback.message.edit_text(
        text='Выберете сервис:',
        reply_markup=main_menu_kb)
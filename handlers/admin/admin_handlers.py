from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.kb_utils import create_inline_kb


admin_handlers = Router()


@admin_handlers.callback_query(F.data == 'admin_panel')
async def admin_panel(callback: CallbackQuery):
    kb = create_inline_kb(1, 'google_settings', 'back_menu')
    await callback.message.edit_text(text='Панель администратора:', reply_markup=kb)

from aiogram import Router, F
from aiogram.types import CallbackQuery

from .reminders import toggle_notification
from keyboards.kb_utils import create_inline_kb
from lexicon.lexicon import LEXICON



notification_handlers = Router()

# Меню настройки уведомлений
@notification_handlers.callback_query(F.data.in_({'setting_notifications', 'turn_on', 'turn_off'}))
async def process_setting_notifications(callback: CallbackQuery):
    current_data = callback.data
    user_id = callback.from_user.id
    status_notification = await toggle_notification(user_id=user_id, status=current_data)

    if status_notification is None:
        await callback.message.edit_text(
            text=LEXICON['error'],
            reply_markup=create_inline_kb(1, 'back_menu'))
        return

    status_text = "включены ✔️" if status_notification else "выключены ❌"
    next_action = 'turn_off' if status_notification else 'turn_on'

    await callback.message.edit_text(text=LEXICON['notifications_menu'].format(status_text),
                                     reply_markup=create_inline_kb(1, next_action, 'services', 'back_menu'))
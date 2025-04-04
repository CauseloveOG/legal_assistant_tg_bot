import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.dao import save_tokens, get_user_info, toggle_google_sync
from keyboards.kb_utils import create_inline_kb
from lexicon.lexicon import LEXICON
from states.states import FSMGoogleAuth
from utils.gcalendar_utils import get_auth_url, exchange_code_for_tokens


google_auth_calendar = Router()


# Обработчик кнопок Google Calendar
@google_auth_calendar.callback_query(F.data.in_({'g_calendar', 'disable_gcalendar_sync', 'enable_gcalendar_sync'}))
async def process_google_calendar(callback: CallbackQuery):
    user = await get_user_info(user_id=callback.from_user.id)
    if user.access_token:
        sync_status = await toggle_google_sync(user_id=callback.from_user.id, status=callback.data)
        button = 'disable_gcalendar_sync' if sync_status else 'enable_gcalendar_sync'
        status_text = "включена ✔️" if sync_status else "выключена ❌"
        text = LEXICON['gcalendar_status'].format(status_text)
    else:
        button = 'connect_gcalendar'
        text = 'Подключите Google calendar'
    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_kb(1, button, 'services', 'back_menu')
    )


# Начало авторизации Google
@google_auth_calendar.callback_query(F.data.in_({'connect_gcalendar', 'google_settings'}))
async def start_google_auth(callback: CallbackQuery, state: FSMContext):
    auth_url = await get_auth_url(callback.from_user.id)
    await callback.message.edit_text(
        'Перейдите по ссылке для подключения Google Calendar:\n'
        f'{auth_url}\n\n'
        'После авторизации введите полученный код в ответное сообщение.',
        reply_markup=create_inline_kb(1, 'services', 'back_menu')
    )
    await state.set_state(FSMGoogleAuth.waiting_for_code)
    await callback.answer()


# Обработка кода авторизации
@google_auth_calendar.message(FSMGoogleAuth.waiting_for_code)
async def process_auth_code(message: Message, state: FSMContext):
    code = message.text.strip()
    try:
        tokens = await exchange_code_for_tokens(code)
        if 'access_token' in tokens:
            await save_tokens(message.from_user.id, tokens)
            await message.answer(text='Google Calendar успешно подключён!',
                                reply_markup=create_inline_kb(1, 'back_menu'))
        else:
            await message.reply(text='Ошибка авторизации. Попробуйте снова.')
    except Exception as e:
        logging.error(f'Ошибка при авторизации Google: {e}')
        await message.answer(text='Произошла ошибка. Попробуйте позже.',
                            reply_markup=create_inline_kb(1, 'back_menu'))
    await state.clear()

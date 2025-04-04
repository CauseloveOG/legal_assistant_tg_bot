import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.dao import set_user
from keyboards.kb_utils import create_inline_kb
from lexicon.lexicon import LEXICON
from config_data.config import Config, load_config

start_handlers = Router()
config: Config = load_config()

# Команда start
@start_handlers.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    await set_user(tg_id=message.from_user.id,
                   username=message.from_user.username,
                   full_name=message.from_user.full_name)
    start_kb = create_inline_kb(1, 'menu')
    await message.answer(text=LEXICON['greeting'],
                         reply_markup=start_kb)


# Команда help
@start_handlers.message(Command(commands='help'))
async def process_help_command(message: Message):
    help_kb = create_inline_kb(1, 'menu')
    await message.answer(text=LEXICON['help'],
                         reply_markup=help_kb)


# Главное меню
@start_handlers.callback_query(F.data.in_({'menu', 'back_menu'}))
async def process_start_button(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    buttons = ['case', 'court_sessions', 'services']
    if user_id == int(config.bot.admin_id):
        buttons.append('admin_panel')
    kb = create_inline_kb(1, *buttons)
    await callback.message.edit_text(
        text=LEXICON['main_menu'].format(callback.from_user.first_name),
        reply_markup=kb)


# Главное меню по команде /menu
@start_handlers.message(Command(commands='menu'))
async def process_start_button(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    buttons = ['case', 'court_sessions', 'services']
    if user_id == int(config.bot.admin_id):
        buttons.append('admin_panel')
    kb = create_inline_kb(1, *buttons)
    await message.answer(
        text=LEXICON['main_menu'].format(message.from_user.first_name),
        reply_markup=kb)
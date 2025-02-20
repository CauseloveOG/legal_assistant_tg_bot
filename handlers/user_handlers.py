from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from numpy.f2py.crackfortran import crackline_re_1

from keyboards.kb_utils import create_inline_kb

router = Router()

@router.message(CommandStart())
async def process_start_command(message: Message):
    start_kb = create_inline_kb(1, 'start')
    await message.answer(text='Legal assistant',
                         reply_markup=start_kb)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer('Help')


@router.callback_query(F.data.in_({'start', 'back'}))
async def process_beginning_command(callback: CallbackQuery):
    main_menu_kb = create_inline_kb(1, 'case', 'court_sessions',
                                    'calendar', 'calculators')
    await callback.message.edit_text(text='Main menu',
                                    reply_markup=main_menu_kb)


@router.callback_query(F.data == 'case')
async def process_case_button(callback: CallbackQuery):
    back_kb = create_inline_kb(1, 'add_case', 'back')
    await callback.message.edit_text(text='Ваши дела:',
                                     reply_markup=back_kb)


@router.callback_query(F.data == 'court_sessions')
async def process_court_sessions_button(callback: CallbackQuery):
    back_kb = create_inline_kb(1, 'back')
    await callback.message.edit_text(text='Ваши заседания: ',
                                     reply_markup=back_kb)


@router.callback_query(F.data == 'calendar')
async def process_calendar_button(callback: CallbackQuery):
    back_kb = create_inline_kb(1, 'back')
    await callback.message.edit_text(text='Каленарь: ',
                                     reply_markup=back_kb)


@router.callback_query(F.data == 'calculators')
async def process_calculators_button(callback: CallbackQuery):
    back_kb = create_inline_kb(1, 'back')
    await callback.message.edit_text(text='Выберете калькулятор: ',
                                     reply_markup=back_kb)
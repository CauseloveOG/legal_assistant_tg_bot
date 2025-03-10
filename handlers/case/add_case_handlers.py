from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.dao import add_case
from keyboards.kb_utils import create_inline_kb
from lexicon.lexicon import LEXICON
from states.states import FSMFillCase, FSMChoiceCase

add_case_handlers = Router()


# Набор функций для добавления дела в БД таблицу cases
# используются состояния на каждое отдельное действие.
#-----------------------------------------------------

# Добавление названия дела
@add_case_handlers.callback_query(StateFilter(FSMChoiceCase.case), F.data == 'add_case')
async def process_add_case_name(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMFillCase.add_case_name)
    await callback.message.edit_text(text=LEXICON['add_case_name'])

# Добавление номера судебного дела
@add_case_handlers.message(StateFilter(FSMFillCase.add_case_name))
async def process_add_case_number(message: Message, state: FSMContext):
    await state.update_data(case_name=message.text)
    await state.set_state(FSMFillCase.add_case_number)
    await message.answer(text=LEXICON['add_court_name'])

# Добавление названия суда
@add_case_handlers.message(StateFilter(FSMFillCase.add_case_number))
async def process_add_court_name(message: Message, state: FSMContext):
    await state.update_data(court_name=message.text)
    await state.set_state(FSMFillCase.add_court_name)
    await message.answer(text=LEXICON['add_case_number'])

# Проверка добавляемого дела
@add_case_handlers.message(StateFilter(FSMFillCase.add_court_name))
async def process_checking_added_case(message: Message, state: FSMContext):
    await state.update_data(case_number=message.text)
    case = await state.get_data()
    await message.answer(text=LEXICON['checking_added'].format(
        case_name=case.get('case_name'),
        court_name=case.get('court_name'),
        case_number=case.get('case_number')),
        reply_markup=create_inline_kb(2, 'confirm_added', 'cancel_added'))

# Уведомление о завершении добавления дела
# с кнопкой о возврате в главное меню.
@add_case_handlers.callback_query(F.data == 'confirm_added')
async def process_add_case_confirm(callback: CallbackQuery, state: FSMContext):
    case = await state.get_data()
    await state.clear()
    await add_case(user_id=callback.from_user.id, case_name=case.get('case_name'),
                   case_number=case.get('case_number'), court_name=case.get('court_name'))
    await callback.message.edit_text(text=LEXICON['successfully_add_case'].format(case.get('case_name')),
                         reply_markup=create_inline_kb(1, 'case', 'back_menu'))

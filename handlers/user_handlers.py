from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.kb_utils import create_inline_kb
from database.database import process_add_user, get_user_cases, add_case_in_db, fetch_chosen_case, delete_case_from_list
from lexicon.lexicon import LEXICON
from states.states import FSMFillCase

router = Router()

# Команда start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await process_add_user(message.from_user.id,
                           message.from_user.username,
                           message.from_user.full_name)
    start_kb = create_inline_kb(1, 'menu')
    await message.answer(text='Legal assistant',
                         reply_markup=start_kb)

# Команда help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer('Help')

# Главное меню
@router.callback_query(F.data == 'menu')
async def process_start_button(callback: CallbackQuery, state: FSMContext):
    main_menu_kb = create_inline_kb(1, 'case', 'court_sessions',
                                    'calendar', 'calculators')
    await callback.message.edit_text(text='Main menu',
                                    reply_markup=main_menu_kb)
    await state.clear()


# Вкладка Дела (Главное меню)
@router.callback_query(F.data.in_({'case', 'yes'}))
async def process_case_button(callback: CallbackQuery, state: FSMContext):
    # Обработка удаления дела
    if callback.data == 'yes':
        await callback.answer(text='Дело удалено')
        case_name =  await state.get_data()
        await delete_case_from_list(callback.from_user.id, case_name['case_name'])
        await state.clear()

    # Получение информации о делах, либо об их отсутствии
    cases: dict[int, dict[str, str | int]] | None = await get_user_cases(callback.from_user.id) # Получение списка дел
    if cases is not None:
        text = LEXICON['not_empty_cases']
        await state.set_state(FSMFillCase.choice_case)
        cases_kb = create_inline_kb(1, *[case['case_name'] for case in cases.values()],
                                    'add_case', 'menu')
    else:
        text = LEXICON['empty_cases']
        cases_kb = create_inline_kb(1, 'add_case', 'menu')
    await callback.message.edit_text(text=text,
                                     reply_markup=cases_kb)


# Вкладка Судебные заседания
@router.callback_query(F.data == 'court_sessions')
async def process_court_sessions_button(callback: CallbackQuery):
    back_kb = create_inline_kb(1, 'menu')
    await callback.message.edit_text(text='Ваши заседания: ',
                                     reply_markup=back_kb)

# Вкладка Календарь
@router.callback_query(F.data == 'calendar')
async def process_calendar_button(callback: CallbackQuery):
    back_kb = create_inline_kb(1, 'menu')
    await callback.message.edit_text(text='Каленарь: ',
                                     reply_markup=back_kb)

# Вкладка Калькулятор
@router.callback_query(F.data == 'calculators')
async def process_calculators_button(callback: CallbackQuery):
    back_kb = create_inline_kb(1, 'menu')
    await callback.message.edit_text(text='Выберете калькулятор: ',
                                     reply_markup=back_kb)

# Набор функций для добавления дела в БД таблицу cases
# используются состояния на каждое отдельное действие.
# Добавление названия дела
@router.callback_query(F.data == 'add_case')
async def process_add_case_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=LEXICON['enter_case_name'])
    await state.set_state(FSMFillCase.add_case_name)

# Добавление номера судебного дела
@router.message(StateFilter(FSMFillCase.add_case_name))
async def process_court_case_name(message: Message, state: FSMContext):
    await state.update_data(case_name=message.text)
    await message.answer(text=LEXICON['court_case_name'])
    await state.set_state(FSMFillCase.add_court_case_name)

# Добавление названия суда
@router.message(StateFilter(FSMFillCase.add_court_case_name))
async def process_court_name(message: Message, state: FSMContext):
    await state.update_data(court_case_name=message.text)
    await message.answer(text=LEXICON['court_name'])
    await state.set_state(FSMFillCase.add_court)

# Уведомление о завершении добавления дела и вывод id нового дела
# с кнопкой о возврате в главное меню.
@router.message(StateFilter(FSMFillCase.add_court))
async def process_add_case(message: Message, state: FSMContext):
    await state.update_data(court=message.text)
    case_id = await add_case_in_db(message.from_user.id, await state.get_data())
    await state.clear()
    back_kb = create_inline_kb(1, 'menu')
    await message.answer(text=f'Готово {case_id}',
                         reply_markup=back_kb)

# Получение информации по запрошенному делу
@router.callback_query(StateFilter(FSMFillCase.choice_case), F.data)
async def get_chosen_case(callback: CallbackQuery, state: FSMContext):
    case_user = await fetch_chosen_case(callback.from_user.id, callback.data)
    await state.update_data(case_name=callback.data)
    print(case_user)
    case_kb = create_inline_kb(1, 'delete_case', 'case', 'menu')
    await callback.message.edit_text(text=case_user,
                                     reply_markup=case_kb)
    await state.set_state(FSMFillCase.case)

# Удаление дела
@router.callback_query(StateFilter(FSMFillCase.case), F.data == 'delete_case')
async def process_delete_case(callback: CallbackQuery, state: FSMContext):
    case_name = await state.get_data()
    case_kb = create_inline_kb(1, 'yes', 'case')
    await callback.message.edit_text(text=f'Хотите удалить дело {case_name['case_name']}?',
                                     reply_markup=case_kb)



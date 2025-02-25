from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime

from keyboards.kb_utils import create_inline_kb
from database.database import (process_add_user, get_user_cases, add_case_in_db,
                               fetch_chosen_case, delete_case_from_list, edit_case_from_list,
                               add_court_date)
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
    await message.answer(text=LEXICON['greeting'],
                         reply_markup=start_kb)

# Команда help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    help_kb = create_inline_kb(1, 'menu')
    await message.answer(text=LEXICON['help'],
                         reply_markup=help_kb)

# Главное меню
@router.callback_query(F.data.in_({'menu', 'back_menu'}))
async def process_start_button(callback: CallbackQuery, state: FSMContext):
    main_menu_kb = create_inline_kb(1, 'case', 'court_sessions',
                                    'calendar', 'calculators')
    await callback.message.edit_text(text=LEXICON['main_menu'].format(callback.from_user.first_name),
                                    reply_markup=main_menu_kb)
    await state.clear()


# Вкладка Мои дела (Главное меню)
@router.callback_query(F.data.in_({'case', 'yes_delete'}))
async def process_case_button(callback: CallbackQuery, state: FSMContext):
    # Вывод дел в случае удаления дела
    if callback.data == 'yes_delete':
        case_name =  await state.get_data()
        await callback.answer(text=await delete_case_from_list(callback.from_user.id, case_name['case_name']))
        await state.clear()

    # Получение информации о делах, либо об их отсутствии
    cases: dict[int, dict[str, str | int]] | None = await get_user_cases(callback.from_user.id) # Получение списка дел
    if cases is not None:
        text = LEXICON['not_empty_cases']
        await state.set_state(FSMFillCase.choice_case)
        cases_kb = create_inline_kb(1, *[case['case_name'] for case in cases.values()],
                                    'add_case', 'back_menu')
    else:
        text = LEXICON['empty_cases']
        cases_kb = create_inline_kb(1, 'add_case', 'back_menu')
    await callback.message.edit_text(text=text,
                                     reply_markup=cases_kb)


# Вкладка Судебные заседания
@router.callback_query(F.data == 'court_sessions')
async def process_court_sessions_button(callback: CallbackQuery):
    back_kb = create_inline_kb(1, 'back_menu')
    await callback.message.edit_text(text='Ваши заседания: ',
                                     reply_markup=back_kb)

# Вкладка Календарь
@router.callback_query(F.data == 'calendar')
async def process_calendar_button(callback: CallbackQuery):
    back_kb = create_inline_kb(1, 'back_menu')
    await callback.message.edit_text(text='Каленарь: ',
                                     reply_markup=back_kb)

# Вкладка Калькулятор
@router.callback_query(F.data == 'calculators')
async def process_calculators_button(callback: CallbackQuery):
    back_kb = create_inline_kb(1, 'back_menu')
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
    await message.answer(text=LEXICON['enter_court_case_name'])
    await state.set_state(FSMFillCase.add_court_case_name)


# Добавление названия суда
@router.message(StateFilter(FSMFillCase.add_court_case_name))
async def process_court_name(message: Message, state: FSMContext):
    await state.update_data(court_case_name=message.text)
    await message.answer(text=LEXICON['enter_court_name'])
    await state.set_state(FSMFillCase.add_court)


# Уведомление о завершении добавления дела
# с кнопкой о возврате в главное меню.
@router.message(StateFilter(FSMFillCase.add_court))
async def process_add_case(message: Message, state: FSMContext):
    await state.update_data(court=message.text)
    case = await state.get_data()
    await add_case_in_db(message.from_user.id, case)
    await state.clear()
    back_kb = create_inline_kb(1, 'back_menu')
    await message.answer(text=LEXICON['successfully_add_case'].format(case['case_name']),
                         reply_markup=back_kb)


# Получение информации по запрошенному делу
@router.callback_query(F.data == 'no_cancel')
@router.callback_query(StateFilter(FSMFillCase.choice_case), F.data)
async def get_chosen_case(callback: CallbackQuery, state: FSMContext):
    if callback.data != 'no_cancel':
        await state.update_data(case_name=callback.data)
    case_name = await state.get_data()
    case_user = await fetch_chosen_case(callback.from_user.id, case_name['case_name'])
    await state.update_data(case_id=case_user[0])
    if case_user:
        case_info = LEXICON['chosen_user_case'].format(name_case=case_user[2], court=case_user[4],
                                                       court_case_name=case_user[3])
        case_kb = create_inline_kb(1, 'add_session_date', 'edit_case',
                                   'delete_case', 'case', 'back_menu')
    else:
        case_info = LEXICON['error']
        case_kb = create_inline_kb(1, 'case', 'back_menu')
    await callback.message.edit_text(text=case_info,
                                     reply_markup=case_kb)
    await state.set_state(FSMFillCase.case)


# Добавление даты судебного заседания
@router.callback_query(StateFilter(FSMFillCase.case), F.data == 'add_session_date')
async def add_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMFillCase.add_court_session)
    await callback.message.edit_text(text=LEXICON['enter_court_session'])

# Обработка введенной даты
@router.message(StateFilter(FSMFillCase.add_court_session))
async def process_date(message: Message, state: FSMContext):
    try:
        date_time = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
        case_id = await state.get_data()
        await add_court_date(case_id['case_id'], date_time)
    except ValueError:
        await message.reply("Неверный формат! Используй: ДД.ММ.ГГГГ ЧЧ:ММ")
    finally:
        await state.clear()
    case_kb = create_inline_kb(1, 'case', 'back_menu')
    await message.answer(text='Дата добавлена',
                         reply_markup=case_kb)


# Редактирование дела
@router.callback_query(StateFilter(FSMFillCase.case), F.data == 'edit_case')
async def process_edit_case(callback: CallbackQuery):
    edit_kb = create_inline_kb(1, 'case_name', 'court', 'court_case_name',
                               'case')
    await callback.message.edit_text(text=LEXICON['choice_edit_case'],
                                     reply_markup=edit_kb)


# Выбор пользователя какой именно параметр необходимо редактировать
@router.callback_query(StateFilter(FSMFillCase.case), F.data.in_({'case_name', 'court',
                                                             'court_case_name'}))
async def process_edit_action(callback: CallbackQuery, state: FSMContext):
    await state.update_data(action=callback.data)
    await state.set_state(FSMFillCase.edit_case)
    await callback.message.edit_text(text='Введите новое значение')


# Обработка редактирования и подтверждение результата
@router.message(StateFilter(FSMFillCase.edit_case))
async def enter_new_value(message: Message, state: FSMContext):
    case_keys = await state.get_data()
    res = await edit_case_from_list(user_id=message.from_user.id, case_name=case_keys['case_name'],
                                    column=case_keys['action'], new_value=message.text)
    kb = create_inline_kb(1, 'case')
    await message.answer(text=res,
                         reply_markup=kb)
    await state.clear()


# Удаление дела
@router.callback_query(StateFilter(FSMFillCase.case), F.data == 'delete_case')
async def process_delete_case(callback: CallbackQuery, state: FSMContext):
    case_name = await state.get_data()
    case_kb = create_inline_kb(1, 'yes_delete', 'no_cancel')
    await callback.message.edit_text(text=LEXICON['confirm_delete'].format(case_name['case_name']),
                                     reply_markup=case_kb)

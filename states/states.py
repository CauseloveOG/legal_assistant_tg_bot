from aiogram.filters.state import State, StatesGroup


class FSMFillCase(StatesGroup):
    add_case_name = State()
    add_court_case_name = State()
    add_court = State()
    choice_case = State()
    case = State()



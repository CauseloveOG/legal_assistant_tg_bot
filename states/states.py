from aiogram.filters.state import State, StatesGroup


class FSMFillCase(StatesGroup):
    add_case_name = State()
    add_case_number = State()
    add_court_name = State()

class FSMChoiceCase(StatesGroup):
    choice_case = State()
    case = State()
    edit_case = State()
    case_note = State()
    communicate_court_session = State()

class FSMGoogleAuth(StatesGroup):
    waiting_for_code = State()


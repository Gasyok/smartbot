from aiogram.fsm.state import State, StatesGroup


class ExecuteCode(StatesGroup):
    code = State()
    macro = State()
    arguments = State()
    add_macros_name = State()
    add_macros_code = State()
    add_macros_params = State()

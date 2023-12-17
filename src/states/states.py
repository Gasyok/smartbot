from aiogram.fsm.state import State, StatesGroup


class ExecuteCode(StatesGroup):
    code = State()
    macro = State()

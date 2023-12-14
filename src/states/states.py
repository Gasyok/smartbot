from aiogram.fsm.state import State, StatesGroup


class ExecuteCode(StatesGroup):
    waiting_for_code = State()
    writing_code = State()

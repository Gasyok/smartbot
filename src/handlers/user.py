from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove
import subprocess
import os
import tempfile
import glob
from aiogram.types import BufferedInputFile


from states.states import ExecuteCode
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Hello! This is SmartBot, paste code And I will help you with it!"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Sorry, I can't help you")


@router.message(StateFilter(None), Command("exec"))
async def cmd_exec(message: Message, state: FSMContext):
    await message.answer(text="Write down the code.")

    await state.set_state(ExecuteCode.writing_code)


@router.message(ExecuteCode.writing_code, F.text)
async def code_done(message: Message, state: FSMContext):
    code = message.text

    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as tmpfile:
        tmpfile.write(code)
        tmpfile_name = tmpfile.name

    try:
        result = subprocess.run(
            ["python", tmpfile_name], capture_output=True, text=True, timeout=5
        )
        output = result.stdout if result.stdout else result.stderr
    except subprocess.TimeoutExpired:
        output = "Timeout bro."
    finally:
        os.remove(tmpfile_name)

    await message.answer(f"Result:\n{output}")
    await state.clear()

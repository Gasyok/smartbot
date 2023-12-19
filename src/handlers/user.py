import random
from aiogram import Router, F
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.types import Message
from aiogram.utils.formatting import (
    Bold,
    as_list,
    as_marked_section,
    as_key_value,
    HashTag,
)
from aiogram import types
import subprocess
import os
import tempfile
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Text, Bold
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile


from keyboards import kb
from states.states import ExecuteCode
from aiogram.fsm.context import FSMContext
from data.macros import macros
from typing import Optional
from aiogram.filters.callback_data import CallbackData
import logging
from handlers.callback import UserMacros
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router()


@router.message(StateFilter(None), Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    content = Text("Hello, ", Bold(message.from_user.full_name))
    content += Text("\nThis is SmartBot!\nCan I help you?")
    await message.answer(**content.as_kwargs())


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Sorry, I can't help you")


@router.message(StateFilter(None), Command("exec"))
async def cmd_exec(message: Message, state: FSMContext):
    await message.answer(text="Write down the code.")
    await state.set_state(ExecuteCode.code)


@router.message(StateFilter(None), Command("macros"))
async def cmd_macros(message: Message, state: FSMContext):
    user_id = int(message.from_user.id) if message.from_user else 0
    info = macros.get_user_macro(user_id)

    list_of_macros = []
    if not info:
        await message.reply("You have 0 macros assigned to you")
        return
    for mac in info:
        list_of_macros.append({"user_id": user_id, "macros_name": str(mac)})

    await message.reply("You got:\n", reply_markup=kb.btns(list_of_macros))
    # await state.set_state("dajfi")

# @router.message(STATEACTION, F.te)


@router.message(StateFilter(None), Command("setmacros"))
async def cmd_setmacros(message: Message, command: CommandObject, state: FSMContext):
    user_id = int(message.from_user.id) if message.from_user else 0
    if command.args is None:
        await message.answer("Error: no arguments")
        return
    try:
        name = command.args.strip()
    except ValueError:
        await message.answer("Format Error. Example:\n" "/setmacros <name>")
        return

    if macros.get_macros_id(user_id, name):
        await message.reply("Macros with this name already exists\n")
        return

    await state.update_data(macros_name=name)

    await message.answer("Write down the code of your macros")
    await state.set_state(ExecuteCode.macro)
    # await ExecuteCode.macro.set()


@router.message(ExecuteCode.macro, F.text)
async def cmd_savemacros(message: Message, state: FSMContext):
    user_id = int(message.from_user.id) if message.from_user else 0
    data = await state.get_data()
    name = data.get("macros_name")
    code = message.text if message.text else ""
    macros.set_user_macro(user_id, name, code)
    await message.answer("Success!")
    await state.clear()


@router.message(ExecuteCode.code, Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await message.answer(text="Canceled state")
    await state.clear()


@router.message(ExecuteCode.code, F.text)
async def code_done(message: Message, state: FSMContext):
    code = message.text if message.text else ""

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "script.py")
        with open(script_path, "w") as script_file:
            script_file.write(code)

        try:
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=tmpdir,
            )
            # result = subprocess.run(
            #     [
            #         "docker",
            #         "run",
            #         "--rm",
            #         "--memory",
            #         "512m",  # Ограничение памяти
            #         "--cpus",
            #         "1.0",  # Ограничение CPU
            #         "-v",
            #         f"{tmpdir}:/app",  # Монтируем tmpdir в контейнер
            #         "code-executor",  # Название вашего Docker-образа
            #     ],
            #     capture_output=True,
            #     text=True,
            #     timeout=30,  # Увеличенное время ожидания для Docker
            # )
            output = result.stdout if result.stdout else result.stderr

            for file in os.listdir(tmpdir):
                if file != "script.py":
                    file_path = os.path.join(tmpdir, file)
                    with open(file_path, "rb") as f:
                        result = await message.answer_document(
                            BufferedInputFile(f.read(), filename=file_path)
                        )

        except subprocess.TimeoutExpired:
            output = "Timeout bro."

    await message.answer(f"Result:\n{output}")
    await state.clear()

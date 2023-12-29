from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from keyboards import kb
from data.macros import macros
from typing import Optional, List
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from states.states import ExecuteCode
import tempfile
import subprocess
from app import logger
import os
import json
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile

# from states.states import ExecuteCode

router = Router()


class UserMacros(CallbackData, prefix="macros"):
    action: str
    user_id: int
    macros_name: str
    arguments: str


@router.callback_query(F.data == "show_list_of_macros")
async def callback_show_list(callback: types.CallbackQuery):
    user_id = int(
        callback.from_user.id) if callback.from_user else None
    if not user_id:
        logger.error("No user")
        return
    info = macros.get_user_macro(user_id)

    list_of_macros = []
    if not info:
        await callback.message.edit_text("You dont have macros assigned to you")
        await callback.answer()
        return

    for mac in info:
        list_of_macros.append({"user_id": user_id, "macros_name": str(mac)})

    await callback.message.edit_text("You got:\n", reply_markup=kb.btns(list_of_macros))
    await callback.answer()


@router.callback_query(F.data == "add_macros")
async def callback_add_macros(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Enter the name of the macros\n")
    await state.set_state(ExecuteCode.add_macros_name)
    await callback.answer()


@router.message(ExecuteCode.add_macros_name, F.text)
async def add_macros_name(message: Message, state: FSMContext):
    user_id = int(message.from_user.id) if message.from_user else None
    if not user_id:
        return
    try:
        msg = message.text.split()
        if len(msg) > 1 or not msg:
            await message.reply("Wrong Format:\n{name}")
            return
    except Exception:
        await message.reply("Wrong Format:\n{name}")
        return
    name = msg[0]
    if macros.get_macros_code(user_id, name)[0]:
        await message.reply("Macros with this name already exists\n")
        return
    await state.update_data(macros_name=name, user_id=user_id)
    await state.set_state(ExecuteCode.add_macros_code)
    await message.reply("Write down the code:\n")


@router.message(ExecuteCode.add_macros_code, F.text)
async def add_macros_code(message: Message, state: FSMContext):
    user_id = int(message.from_user.id) if message.from_user else None
    data = await state.get_data()
    if not user_id or user_id != data.get("user_id"):
        return
    name = data.get("macros_name")
    code = str(message.text) if message.text else ""
    await state.update_data(code=code)
    await state.set_state(ExecuteCode.add_macros_params)
    await message.reply("Choose the output:\n", reply_markup=kb.btns_output_format())


@router.callback_query(F.data == "output_file", ExecuteCode.add_macros_params)
async def output_file(callback: types.CallbackQuery, state: FSMContext):
    params = {
        "output": "file"
    }
    await state.update_data(params=params)
    await callback.message.edit_text("Type any other params, (JSON formatted msg) or type <NONE>")
    await callback.answer()


@router.callback_query(F.data == "output_stdout", ExecuteCode.add_macros_params)
async def output_stdout(callback: types.CallbackQuery, state: FSMContext):
    params = {
        "output": "stdout"
    }
    await state.update_data(params=params)
    await callback.message.edit_text("Type any other params, (JSON formatted msg) or type <NONE>")
    await callback.answer()


@router.message(ExecuteCode.add_macros_params, F.text)
async def add_macros_params(message: Message, state: FSMContext):
    user_id = int(message.from_user.id) if message.from_user else None
    data = await state.get_data()
    if not user_id or user_id != data.get("user_id"):
        logger.error("No user match")
        return
    name = data.get("macros_name")
    code = data.get("code")
    out_params = data.get("params")
    out_params = out_params if isinstance(out_params, dict) else {}

    user_params = dict()
    if message.text and message.text.capitalize() != "None":
        try:
            user_params = json.loads(str(message.text))
        except Exception:
            await message.reply("Wrong Format:\nJSON format params")
            return

    check = set(out_params.keys()) & set(user_params.keys())
    if check:
        await message.reply("Wrong Params, try again\n")
        return

    params = {**out_params, **user_params}

    macros.set_user_macro(user_id, name, code, params)
    await message.answer("Possibly Success!\nCheck your macros;)")
    await state.clear()


@router.callback_query(UserMacros.filter())
async def callbacks_macros(
    callback: types.CallbackQuery,
    callback_data: UserMacros,
    state: FSMContext
):
    user_id = callback_data.user_id
    macros_name = callback_data.macros_name
    action = callback_data.action
    arguments = callback_data.arguments.split()
    await state.update_data(user_macros=callback_data)

    match action:
        case "Show":
            await callback.message.edit_text(
                "Choose:\n",
                reply_markup=kb.btns_action(callback_data)
            )
        case "Code":
            code = macros.get_macros_code(user_id, macros_name)[0]
            await callback.message.edit_text(
                f"Your Code below:\n{code}"
            )
        case "Run":
            await callback.message.edit_text(
                f"Do you want to add arguments to code?:\n",
                reply_markup=kb.btns_run_arguments(callback_data)
            )
        case "Edit":
            await state.set_state(ExecuteCode.editcode)
            await callback.message.edit_text(
                "Enter the new script\n"
            )
        case "None":
            await callback.message.edit_text(
                f"Choose Format:\n",
                reply_markup=kb.btns_run_format(callback_data)
            )
        case "Enter":
            await state.set_state(ExecuteCode.arguments)
            await callback.message.edit_text(
                "Enter the arguments\n"
            )

    if action == "Stdout" or action == "File":
        code = macros.get_macros_code(user_id, macros_name)[0]
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "script.py")
            with open(script_path, "w") as script_file:
                script_file.write(code)

            try:
                command = ["python", script_path] + arguments
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=tmpdir,
                )
                output = result.stdout if result.stdout else result.stderr

                if action == "File":
                    stdout_file_path = os.path.join(tmpdir, "stdout.txt")
                    with open(stdout_file_path, "w") as stdout_file:
                        stdout_file.write(output)

                    if len(os.listdir(tmpdir)) > 10:
                        await callback.message.edit_text(
                            "You Dont have any files or there are too many of them\n"
                        )
                    for file in os.listdir(tmpdir):
                        if file != "script.py":
                            file_path = os.path.join(tmpdir, file)
                            with open(file_path, "rb") as f:
                                await callback.message.answer_document(
                                    BufferedInputFile(
                                        f.read(), filename=file_path)
                                )
                    await callback.answer()
                    return

            except subprocess.TimeoutExpired:
                output = "Timeout bro."

        await callback.message.answer(
            f"Your stdout\n{output}"
        )

    await callback.answer()


@router.message(ExecuteCode.arguments, F.text)
async def cmd_getarguments(message: Message, state: FSMContext):
    list_of_arguments = message.text
    data = await state.get_data()
    user_macros = data.get("user_macros")
    user_macros.arguments = list_of_arguments
    await message.reply(
        text="Choose Format with your arguments\n",
        reply_markup=kb.btns_run_format(user_macros)
    )
    await state.clear()

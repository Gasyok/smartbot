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
import os
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
    user_id = int(message.from_user.id) if message.from_user else 0
    info = macros.get_user_macro(user_id)

    list_of_macros = []
    if not info:
        await message.reply("You have 0 macros assigned to you")
        return
    for mac in info:
        list_of_macros.append({"user_id": user_id, "macros_name": str(mac)})

    await message.reply("You got:\n", reply_markup=kb.btns(list_of_macros))


# @router.callback_query(F.data == "add_macros")
# async def callback_add_macros(callback: types.CallbackQuery):


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

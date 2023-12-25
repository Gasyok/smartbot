from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from keyboards import kb
from data.macros import macros
from typing import Optional
from aiogram.filters.callback_data import CallbackData
import logging
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


@router.callback_query(UserMacros.filter())
async def callbacks_macros(
    callback: types.CallbackQuery,
    callback_data: UserMacros
):
    user_id = callback_data.user_id
    macros_name = callback_data.macros_name
    action = callback_data.action

    match action:
        case "Show":
            await callback.message.edit_text(
                "Choose:\n",
                reply_markup=kb.btns_action(callback_data)
            )
        case "Code":
            code = macros.get_macros_id(user_id, macros_name)
            await callback.message.edit_text(
                f"Your Code below:\n{code}"
            )
        case "Run":
            await callback.message.edit_text(
                f"Choose Format:\n",
                reply_markup=kb.btns_run_format(callback_data)
            )

    if action == "Stdout" or action == "File":
        code = macros.get_macros_id(user_id, macros_name)
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
                                    BufferedInputFile(f.read(), filename=file_path)
                                )
                    await callback.answer()
                    return

            except subprocess.TimeoutExpired:
                output = "Timeout bro."

        await callback.message.answer(
            f"Your stdout\n{output}"
        )

    await callback.answer()

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
import subprocess
import os
import tempfile
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Text, Bold
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile


from states.states import ExecuteCode
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    # ans = "Hello! This is SmartBot, paste code And I will help you with it!"
    content = Text("Hello, ", Bold(message.from_user.full_name))
    content += Text("\nThis is SmartBot!")
    await message.answer(**content.as_kwargs())
    # await message.answer(ans)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Sorry, I can't help you")


@router.message(StateFilter(None), Command("exec"))
async def cmd_exec(message: Message, state: FSMContext):
    await message.answer(text="Write down the code.")

    await state.set_state(ExecuteCode.writing_code)


@router.message(F.text, Command("test"))
async def cmd_test(message: Message):
    code = message.text
    await message.answer(f"Hi, {code}", parse_mode=ParseMode.MARKDOWN_V2)


@router.message(ExecuteCode.writing_code, F.text)
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
                cwd=tmpdir,  # Устанавливаем временный dir как рабочий dir
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

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Hello! This is SmartBot, paste code And I will help you with it!"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Sorry, I can't help you :(")

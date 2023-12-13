from aiogram.filters.command import Command
from aiogram import types

from src.main import dp, bot
from src.config import config


@dp.message_handler(Command("start"))
async def start(message: Message):
    await bot.send_message(message.chat.id, "Добро пожаловать!!!")

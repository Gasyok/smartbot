from aiogram import Bot, Dispatcher
from .cfg import TOKEN

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

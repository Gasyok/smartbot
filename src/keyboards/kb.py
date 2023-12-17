from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types
from handlers.callback import UserMacros
# import json


def btns(macros: list):
    kb = InlineKeyboardBuilder()
    for macro in macros:
        kb.button(text=macro["macros_name"], callback_data=UserMacros(user_id=macro.get("user_id"), macros_name=macro.get("macros_name")))

    return kb.as_markup(resize_keyboard=True)

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types
from handlers.callback import UserMacros


def btns(macros: list):
    kb = InlineKeyboardBuilder()
    for macro in macros:
        kb.button(
            text=macro.get("macros_name"),
            callback_data=UserMacros(
                user_id=macro.get("user_id"),
                macros_name=macro.get("macros_name")
            ).pack()
        )

    return kb.as_markup()

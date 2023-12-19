from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from keyboards import kb
from data.macros import macros
from typing import Optional
from aiogram.filters.callback_data import CallbackData
import logging

# from states.states import ExecuteCode

router = Router()


class UserMacros(CallbackData, prefix="macros"):
    user_id: int
    macros_name: str


@router.callback_query(UserMacros.filter())
async def callbacks_macros(
    callback: types.CallbackQuery,
    callback_data: UserMacros
):
    user_id = callback_data.user_id
    macros_name = callback_data.macros_name
    code = macros.get_macros_id(user_id, macros_name)
    await callback.message.edit_text(f"Your code:\n {code}")
    await callback.answer()

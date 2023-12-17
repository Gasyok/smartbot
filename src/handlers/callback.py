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


# @router.callback_query(F.data)
# async def callback_answer(callback: CallbackQuery):
#     # {"user_id":, "macros_name":}
#     # data = dict(F.data)
#     # print(data)
#     # await callback.answer(data)
#     user_id = data["user_id"]
#     macros_name = data["macros_name"]
#     code = macros.get_macros_id(user_id, macros_name)
#     if not code:
#         code = ""

#     await callback.answer(str(code))


@router.callback_query(UserMacros.filter())
async def callbacks_user_macros(
        callback: types.CallbackQuery,
        callback_data: UserMacros
):
    user_id = callback_data.user_id
    macros_name = callback_data.macros_name

    code = macros.get_macros_id(user_id, macros_name)
    if not code:
        code = "Nothing"

    logging.info("HIEL")
    # await Message.answer("HI")
    await callback.message.answer(str(code))
    await callback.answer(str(code))

    # if callback_data.action == "change":
    #     user_data[callback.from_user.id] = user_value + callback_data.value
    #     await update_num_text_fab(callback.message, user_value + callback_data.value)
    # else:
    #     await callback.message.edit_text(f"Итого: {user_value}")
    # await callback.answer()

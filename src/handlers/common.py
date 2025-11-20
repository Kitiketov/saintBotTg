from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import base64
from src.keyboards import keyboards
from src.texts import text
from src.states.states import Gen, CallbackFactory, RemoveCallbackFactory
from src.db import db
from src.utilities import utils


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)

@router.callback_query(CallbackFactory.filter(F.action == "cancel"))
async def cancel(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    if callback_data.room_iden == "None":
        await state.clear()
    await call.message.delete()


@router.message(F.text == "◀️Вернуться в меню")
@router.callback_query(CallbackFactory.filter(F.action == "back_to_menu"))
async def menu(call: CallbackQuery, callback_data: CallbackFactory):
    await db.update_user(call.from_user)
    await call.message.edit_text("Меню", reply_markup=keyboards.choice_kb)

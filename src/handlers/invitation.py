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
import logging

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


@router.callback_query(CallbackFactory.filter(F.action == "create_invitation"))
async def create_invitation(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "MEMBER NOT EXISTS":
        await call.message.edit_text(f"Вы не участник комнаты  {room_name}",
                                     reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))
        return

    elif isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {room_name} не существует",
                                     reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))
        return

    kb = await keyboards.join_to_room(callback_data.room_iden)

    await call.message.answer(
        f"✉️Приглашение принять участвие в Тайном санта в комнате {room_name}\n<i>Если приглашение не сработало попробуйте присоединиться в ручном режиме</i>",
        reply_markup=kb)


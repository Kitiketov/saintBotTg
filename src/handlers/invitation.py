from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.db import db
from src.keyboards import common_kb, invitation_kb
from src.states.states import CallbackFactory
from src.texts import messages
from src.texts.callback_actions import CallbackAction


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


@router.callback_query(
    CallbackFactory.filter(F.action == CallbackAction.CREATE_INVITATION)
)
async def create_invitation(
    call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(
        call.from_user.id, callback_data.room_iden
    )
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "MEMBER NOT EXISTS":
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    elif isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return
    info = await call.bot.get_me()
    kb = await invitation_kb.join_to_room_kb(callback_data.room_iden, info.username)

    await call.message.answer(messages.invitation_text(room_name), reply_markup=kb)

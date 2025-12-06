from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.db import db
from src.keyboards import common_kb, invitation_kb, room_admin_kb
from src.states.states import Gen, CallbackFactory
from src.texts import messages
from src.texts.callback_actions import CallbackAction
from src.handlers.common import get_room_name


router = Router(name=__name__)


@router.callback_query(
    CallbackFactory.filter(F.action == CallbackAction.CUSTOM_INVITATION)
)
async def custom_invitation(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
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

    await state.set_state(Gen.set_custom_invitation)
    await state.set_data({"room_iden": callback_data.room_iden})

    await call.message.answer(
        messages.prompt_custom_invitation(room_name),
        reply_markup=await common_kb.cancel_kb("None", asAdmin=True),
    )


@router.message(Gen.set_custom_invitation)
async def set_custom_invitation(msg: Message, state: FSMContext):
    data = await state.get_data()
    room_iden = data.get("room_iden")

    if msg.text == "🚫Отмена":
        await state.clear()
        if room_iden:
            room_name = await get_room_name(room_iden)
            await msg.answer(
                messages.room_admin_title(room_name),
                reply_markup=await room_admin_kb.room_admin_kb(room_iden),
            )
        else:
            await msg.answer(messages.menu(), reply_markup=common_kb.choice_kb)
        return

    if msg.media_group_id:
        await msg.answer(
            messages.media_group_not_supported(),
            reply_markup=await common_kb.cancel_kb("None", asAdmin=True),
        )
        return

    if not room_iden:
        await state.clear()
        await msg.answer(messages.menu(), reply_markup=common_kb.choice_kb)
        return

    access = await db.check_room_and_member(msg.from_user.id, room_iden)
    room_name = await get_room_name(room_iden)
    if access == "ROOM NOT EXISTS":
        await state.clear()
        await msg.answer(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if access == "MEMBER NOT EXISTS":
        await state.clear()
        await msg.answer(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    raw_text = msg.text or msg.caption or ""
    if not raw_text and not msg.photo:
        await msg.answer(
            messages.invitation_empty(),
            reply_markup=await common_kb.cancel_kb("None", asAdmin=True),
        )
        return

    invitation_text = raw_text.replace("\\", "/").replace("'", "`").replace('"', "`")
    manual_join = f"Если приглашение не сработало попробуйте присоединиться в ручном режиме <code>{room_name}</code>"

    if invitation_text.strip():
        full_text = f"{invitation_text}\n\n{manual_join}"
    else:
        full_text = manual_join

    limit = 1024 if msg.photo else 4096
    if len(full_text) > limit:
        await msg.answer(
            messages.invitation_too_long(),
            reply_markup=await common_kb.cancel_kb("None", asAdmin=True),
        )
        return

    info = await msg.bot.get_me()
    kb = await invitation_kb.join_to_room_kb(room_iden, info.username)

    await state.clear()
    if msg.photo:
        await msg.answer_photo(
            photo=msg.photo[-1].file_id, caption=full_text, reply_markup=kb
        )
        return

    await msg.answer(full_text, reply_markup=kb)

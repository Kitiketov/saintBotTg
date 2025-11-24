from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.config import settings, logger
from src.db import db
from src.keyboards import common_kb, room_member_kb
from src.states.states import Gen, CallbackFactory
from src.texts import messages, text
from src.texts.callback_actions import CallbackAction


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.MY_WISHES))
async def my_wishes(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    isMemberOrAdmin = await db.check_room_and_member(
        call.from_user.id, callback_data.room_iden
    )

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        room_name = await get_room_name(callback_data.room_iden)
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    status, wishes, photo_id = await db.get_wishes_and_photo(
        callback_data.room_iden, call.from_user.id
    )
    wishes_info = await text.create_wishes_info(wishes)
    kb = await room_member_kb.wishes_kb(callback_data.room_iden, asAdmin=False)
    if photo_id:
        await call.message.answer_photo(
            photo=photo_id, caption=wishes_info, reply_markup=kb
        )
        return
    await call.message.answer(wishes_info, reply_markup=kb)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.EDIT_WISHES))
async def my_wishes(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    isMemberOrAdmin = await db.check_room_and_member(
        call.from_user.id, callback_data.room_iden
    )

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        room_name = await get_room_name(callback_data.room_iden)
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if isMemberOrAdmin != True:
        await call.message.edit_text(
            messages.wish_not_member(),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    status, wishes, photo_id = await db.get_wishes_and_photo(
        callback_data.room_iden, call.from_user.id
    )

    if status in ("ROOM NOT EXISTS", "MEMBER NOT EXISTS"):
        await call.message.edit_text(
            messages.wish_not_member(),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    await state.set_data({"room_iden": callback_data.room_iden})
    await state.set_state(Gen.set_wishes)

    kb = await common_kb.cancel_kb("None", asAdmin=False)
    answer = messages.prompt_wish_with_current(wishes)

    if photo_id:
        await call.message.answer_photo(photo=photo_id, caption=answer, reply_markup=kb)
        return
    await call.message.answer(
        answer,
        reply_markup=kb,
    )


@router.message(Gen.set_wishes)
async def edit_wishes_room(msg: Message, state: FSMContext):
    wishes_raw = msg.text or msg.caption or ""

    data = await state.get_data()
    room_iden = data.get("room_iden")
    await state.clear()

    if msg.text == "🚫Отмена":
        await msg.answer(messages.menu(), reply_markup=common_kb.choice_kb)
        return

    if msg.media_group_id:
        await msg.answer(
            messages.media_group_not_supported(),
            reply_markup=await common_kb.cancel_kb("None", False),
        )
        return

    edit_wishes = wishes_raw.replace("\\", "/").replace("'", "`").replace('"', "`")
    if msg.photo:
        if settings.chat_id:
            try:
                await msg.bot.send_photo(
                    chat_id=settings.chat_id, photo=msg.photo[-1].file_id
                )
            except Exception as e:
                logger.error(f"Error sending photo to chat {settings.chat_id}: {e}")
                pass
        room_status = await db.edit_wishes(
            edit_wishes, msg.from_user.id, room_iden, msg.photo[-1].file_id
        )
    else:
        room_status = await db.edit_wishes(edit_wishes, msg.from_user.id, room_iden)
    if room_status == "ROOM NOT EXISTS":
        await msg.answer(
            messages.room_not_exists(),
            reply_markup=await common_kb.ok_kb("None", False),
        )
        return

    if room_status == "MEMBER NOT EXISTS":
        await msg.answer(
            messages.wish_not_member(),
            reply_markup=await common_kb.ok_kb("None", False),
        )
        return
    wishes_info = messages.wish_updated(edit_wishes)
    await state.clear()
    kb = await room_member_kb.wishes_kb(room_iden, asAdmin=False)
    if msg.photo:
        await msg.answer_photo(
            photo=msg.photo[-1].file_id, caption=wishes_info, reply_markup=kb
        )
        return
    await msg.answer(
        wishes_info,
        reply_markup=kb,
    )


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.SEE_WISHES))
async def see_wishes(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    isMemberOrAdmin = await db.check_room_and_member(
        call.from_user.id, callback_data.room_iden
    )

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        room_name = await get_room_name(callback_data.room_iden)
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    member_id = await db.who_gives(callback_data.room_iden, call.from_user.id)
    status, wishes, photo_id = await db.get_wishes_and_photo(
        callback_data.room_iden, member_id
    )
    wishes_info = await text.take_wishes_info(wishes)

    kb = await common_kb.ok_kb("None", asAdmin=False)

    if photo_id:
        await call.message.answer_photo(
            photo=photo_id, caption=wishes_info, reply_markup=kb
        )
        return

    await call.message.answer(wishes_info, reply_markup=kb)

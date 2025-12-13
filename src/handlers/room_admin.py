from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.config import RATE_LIMIT_DELAY
from src.db import db
from src.handlers.common import EFFECT_IDS
from src.keyboards import common_kb, room_admin_kb
from src.states.states import CallbackFactory, RemoveCallbackFactory
from src.texts import messages
from src.texts.callback_actions import CallbackAction
from src.utilities import notification
from src.utilities import utils


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


async def _perform_start_event(call, room_iden, room_name: str, include_admin: bool):
    status = await db.isStarted(room_iden)
    if status:
        await call.message.edit_text(
            messages.event_already_started(room_name),
            reply_markup=await room_admin_kb.room_admin_kb(room_iden),
        )
        return

    members, admin, isAdminMember = await db.get_members_list(room_iden)
    if isAdminMember:
        members.append(admin)
    elif include_admin:
        members.append(admin)

    members = [member[0] for member in members]
    if len(members) < 2:
        await call.message.edit_text(
            messages.event_not_enough_members(room_name),
            reply_markup=await room_admin_kb.room_admin_kb(room_iden),
        )
        return

    await db.start_event(room_iden)
    pairs = utils.randomize_members(members)
    await db.write_pairs(pairs, room_iden)
    await call.message.edit_text(
        messages.event_started(room_name),
        reply_markup=await room_admin_kb.room_admin_kb(room_iden),
    )
    await notification.broadcast(
        call.bot,
        members,
        text=messages.event_started_notify(room_name),
        reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        delay=RATE_LIMIT_DELAY,
        message_effect_id=EFFECT_IDS["🎉"],
    )
    await call.answer("Уведомление о начале события отправлено")


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.DELETE_ROOM))
async def delete_room(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    isMemberOrAdmin = await db.check_room_and_member(
        call.from_user.id, callback_data.room_iden
    )
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    kb = await room_admin_kb.confirm_kb(callback_data.room_iden, callback_data.asAdmin)
    await call.message.answer(
        messages.room_leave_confirmation(room_name), reply_markup=kb
    )


@router.callback_query(
    CallbackFactory.filter(F.action == CallbackAction.CONFIRM_DELETE)
)
async def delete_room(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    isMemberOrAdmin = await db.check_room_and_member(
        call.from_user.id, callback_data.room_iden
    )
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    await db.delete_room(callback_data.room_iden, call.from_user.id)
    await call.message.edit_text(
        messages.room_deleted(room_name), reply_markup=common_kb.choice_kb
    )


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.REMOVE_MEMBER))
async def remove_member(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    members, *_ = await db.get_members_list(callback_data.room_iden)

    kb = await room_admin_kb.member_kb(members, callback_data.room_iden)
    await call.message.answer(messages.choose_option(), reply_markup=kb)


@router.callback_query(
    RemoveCallbackFactory.filter(F.action == CallbackAction.REMOVE_MEMBER)
)
async def removing_member(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    isMemberOrAdmin = await db.check_room_and_member(
        callback_data.user_id, callback_data.room_iden
    )
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "MEMBER NOT EXISTS":
        await call.message.edit_text(
            messages.member_already_removed(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    await db.leave_room(callback_data.room_iden, callback_data.user_id)
    await call.message.edit_text(
        messages.member_removed(room_name),
        reply_markup=await common_kb.ok_kb(callback_data.room_iden, asAdmin=True),
    )


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.START_EVENT))
async def start_event(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    isMemberOrAdmin = await db.check_room_and_member(
        call.from_user.id, callback_data.room_iden
    )
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    room_admin_id = await db.get_room_admin(callback_data.room_iden)
    if room_admin_id != call.from_user.id:
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if isMemberOrAdmin == "MEMBER NOT EXISTS":
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    status = await db.isStarted(callback_data.room_iden)
    if status:
        await call.message.edit_text(
            messages.event_already_started(room_name),
            reply_markup=await room_admin_kb.room_admin_kb(callback_data.room_iden),
        )
        return

    members, admin, isAdminMember = await db.get_members_list(callback_data.room_iden)
    if isMemberOrAdmin == "IS ADMIN" and not isAdminMember:
        kb = await room_admin_kb.start_event_confirm_kb(callback_data.room_iden)
        await call.message.edit_text(
            messages.admin_not_member_start(room_name),
            reply_markup=kb,
        )
        return

    await _perform_start_event(
        call,
        callback_data.room_iden,
        room_name,
        include_admin=isAdminMember,
    )


@router.callback_query(
    CallbackFactory.filter(F.action == CallbackAction.START_EVENT_JOIN_ADMIN)
)
async def start_event_join_admin(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    room_name = await get_room_name(callback_data.room_iden)
    room_admin_id = await db.get_room_admin(callback_data.room_iden)
    if room_admin_id != call.from_user.id:
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    status = await db.isStarted(callback_data.room_iden)
    if status:
        await call.message.edit_text(
            messages.event_already_started(room_name),
            reply_markup=await room_admin_kb.room_admin_kb(callback_data.room_iden),
        )
        return

    join_status = await db.connect2room(room_name, call.from_user.id)
    if join_status == "room_error":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return
    if join_status == "joined late":
        await call.message.edit_text(
            messages.event_already_started(room_name),
            reply_markup=await room_admin_kb.room_admin_kb(callback_data.room_iden),
        )
        return

    await _perform_start_event(
        call,
        callback_data.room_iden,
        room_name,
        include_admin=True,
    )


@router.callback_query(
    CallbackFactory.filter(F.action == CallbackAction.START_EVENT_SKIP_ADMIN)
)
async def start_event_skip_admin(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    room_name = await get_room_name(callback_data.room_iden)
    room_admin_id = await db.get_room_admin(callback_data.room_iden)
    if room_admin_id != call.from_user.id:
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    await _perform_start_event(
        call,
        callback_data.room_iden,
        room_name,
        include_admin=False,
    )


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.REMIND_ABOUT_EVENT))
async def remind_about_event(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    isMemberOrAdmin = await db.check_room_and_member(
        call.from_user.id, callback_data.room_iden
    )
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if isMemberOrAdmin == "MEMBER NOT EXISTS":
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    status = await db.isStarted(callback_data.room_iden)
    if not status:
        await call.message.edit_text(
            messages.event_not_started(room_name),
            reply_markup=await room_admin_kb.room_admin_kb(callback_data.room_iden),
        )
        return

    members, admin, isAdminMember = await db.get_members_list(callback_data.room_iden)
    if isAdminMember:
        members.append(admin)

    members = [member[0] for member in members]
    await notification.broadcast(call.bot, members,
                                 text=messages.remind_notify(room_name),
                                 reply_markup=await common_kb.ok_kb("None", asAdmin=False),
                                 delay=RATE_LIMIT_DELAY,
                                 )
    await call.answer("Напоминание отправлено")

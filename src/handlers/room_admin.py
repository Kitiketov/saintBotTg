from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import base64
from src.db import db
from src.keyboards import keyboards
from src.states.states import CallbackFactory, RemoveCallbackFactory
from src.texts import messages, text
from src.texts.callback_actions import CallbackAction
from src.utilities import utils

async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)



@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.DELETE_ROOM))
async def delete_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )
        return

    kb = await keyboards.confirm_keyboard(callback_data.room_iden, callback_data.asAdmin)
    await call.message.answer(messages.room_leave_confirmation(room_name), reply_markup=kb)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.CONFIRM_DELETE))
async def delete_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )
        return

    await db.delete_room(callback_data.room_iden, call.from_user.id)
    await call.message.edit_text(messages.room_deleted(room_name), reply_markup=keyboards.choice_kb)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.REMOVE_MEMBER))
async def remove_member(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    members, *_ = await db.get_members_list(callback_data.room_iden)

    kb = await keyboards.member_keyboard(members, callback_data.room_iden)
    await call.message.answer(messages.choose_option(), reply_markup=kb)


@router.callback_query(RemoveCallbackFactory.filter(F.action == CallbackAction.REMOVE_MEMBER))
async def removing_member(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(callback_data.user_id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "MEMBER NOT EXISTS":
        await call.message.edit_text(
            messages.member_already_removed(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )
        return

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )
        return

    await db.leave_room(callback_data.room_iden, callback_data.user_id)
    await call.message.edit_text(
        messages.member_removed(room_name),
        reply_markup=await keyboards.ok_keyboard(callback_data.room_iden, asAdmin=True),
    )


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.START_EVENT))
async def start_event(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )
        return

    status = await db.isStarted(callback_data.room_iden)
    if status:
        await call.message.edit_text(
            messages.event_already_started(room_name),
            reply_markup=await keyboards.room_admin_keyboard(callback_data.room_iden),
        )
        return

    members, admin, isAdminMember = await db.get_members_list(callback_data.room_iden)
    if isAdminMember:
        members.append(admin)

    members = [member[0] for member in members]
    if len(members) < 2:
        await call.message.edit_text(
            messages.event_not_enough_members(room_name),
            reply_markup=await keyboards.room_admin_keyboard(callback_data.room_iden),
        )
        return

    await db.start_event(callback_data.room_iden)
    pairs = utils.randomize_members(members)
    await db.write_pairs(pairs, callback_data.room_iden)
    await call.message.edit_text(
        messages.event_started(room_name),
        reply_markup=await keyboards.room_admin_keyboard(callback_data.room_iden),
    )

    for user_id in members:
        await call.bot.send_message(
            chat_id=user_id,
            text=messages.event_started_notify(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )

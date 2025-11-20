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



@router.callback_query(CallbackFactory.filter(F.action == "delete_room"))
async def delete_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {room_name} не существует",
                                     reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))
        return

    kb = await keyboards.confirm_keyboard(callback_data.room_iden, callback_data.asAdmin)
    await call.message.answer(f"Вы уверены что хотите удалить комнату {room_name} ?", reply_markup=kb)


@router.callback_query(CallbackFactory.filter(F.action == "confirm_delete"))
async def delete_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {room_name} не существует",
                                     reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))
        return

    await db.delete_room(callback_data.room_iden, call.from_user.id)
    await call.message.edit_text(f"Комната {room_name} удаленна", reply_markup=keyboards.choice_kb)


@router.callback_query(CallbackFactory.filter(F.action == "remove_member"))
async def remove_member(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    members, *_ = await db.get_members_list(callback_data.room_iden)

    kb = await keyboards.member_keyboard(members, callback_data.room_iden)
    await call.message.answer("Выберите нужный вам вариант", reply_markup=kb)


@router.callback_query(RemoveCallbackFactory.filter(F.action == "remove_member"))
async def removing_member(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(callback_data.user_id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "MEMBER NOT EXISTS":
        await call.message.edit_text(f"Участник уже не в {room_name}",
                                     reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))
        return

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {room_name} не существует ",
                                     reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))
        return

    await db.leave_room(callback_data.room_iden, callback_data.user_id)
    await call.message.edit_text(f"Участник удален из комнаты  {room_name} ",
                                 reply_markup=await keyboards.ok_keyboard(callback_data.room_iden, asAdmin=True))


@router.callback_query(CallbackFactory.filter(F.action == "start_event"))
async def start_event(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {room_name} не существует",
                                     reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))
        return

    status = await db.isStarted(callback_data.room_iden)
    if status:
        await call.message.edit_text(f"Событие уже начато  {room_name} ",
                                     reply_markup=await keyboards.room_admin_keyboard(callback_data.room_iden))
        return

    members, admin, isAdminMember = await db.get_members_list(callback_data.room_iden)
    if isAdminMember:
        members.append(admin)

    members = [member[0] for member in members]
    if len(members) < 2:
        await call.message.edit_text(f"Участников в  {room_name} недостаточно для начала. Должно быть более 1",
                                     reply_markup=await keyboards.room_admin_keyboard(callback_data.room_iden))
        return

    await db.start_event(callback_data.room_iden)
    pairs = utils.randomize_members(members)
    await db.write_pairs(pairs, callback_data.room_iden)
    await call.message.edit_text(f"Событие началось в  {room_name} ",
                                 reply_markup=await keyboards.room_admin_keyboard(callback_data.room_iden))

    for user_id in members:
        await call.bot.send_message(chat_id=user_id,
                                    text=f"Событие в комнате {room_name} началось\nПроверте кому вы дарите",
                                    reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))

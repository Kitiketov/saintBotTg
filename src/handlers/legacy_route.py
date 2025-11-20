import base64

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.db import db
from src.keyboards import keyboards
from src.states.states import CallbackFactory
from src.texts import messages, text
from src.texts.callback_actions import CallbackAction


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


@router.message(Command("menu"))
@router.message(Command("start"))
async def start_handler(msg: Message):
    await db.add_user(msg.from_user)
    if not ("join_to_room-" in msg.text and "end_invitation" in msg.text):
        await msg.answer(messages.welcome_menu(), reply_markup=keyboards.choice_kb)
        return

    raw_iden = msg.text.split("join_to_room-")[1].replace("end_invitation", "")
    room_iden = base64.urlsafe_b64decode(raw_iden + "===").decode()

    name = await get_room_name(room_iden)
    room_status = await db.connect2room(name, msg.from_user.id)

    if room_status == "room_error":
        await msg.answer(messages.room_not_exists(), reply_markup=await keyboards.cancel_keyboard("None", False))
        return

    if room_status == "user_error":
        await msg.answer(
            messages.user_already_in_room(),
            reply_markup=await keyboards.cancel_keyboard("None", False),
        )
        return

    if room_status == "joined late":
        await msg.answer(messages.game_already_started(), reply_markup=await keyboards.cancel_keyboard("None", False))
        return

    kb = await keyboards.room_member_keyboard(f"{''.join(name.split(':'))}")
    await msg.answer(messages.join_success(msg.from_user.first_name, name), reply_markup=kb)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.REFRESH_LIST))
@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.MEMBERS_LIST))
async def get_member_list(call: CallbackQuery, callback_data: CallbackFactory):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "MEMBER NOT EXISTS" or (callback_data.asAdmin == False and isMemberOrAdmin == "IS ADMIN"):
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )
        return

    elif isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )
        return

    if callback_data.action == CallbackAction.REFRESH_LIST:
        await call.bot.delete_message(call.from_user.id, call.message.message_id)

    member_list, admin, isAdminMember = await db.get_members_list(callback_data.room_iden)
    if isAdminMember:
        member_list.append(admin)
    ans = await text.create_member_list(member_list, admin, callback_data.room_iden)
    await call.message.answer(
        ans, reply_markup=await keyboards.refresh_list_kb(callback_data.room_iden, callback_data.asAdmin)
    )


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.LEAVE_ROOM))
async def cancel(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    await db.leave_room(callback_data.room_iden, call.from_user.id)
    await call.message.edit_text(messages.left_room(), reply_markup=keyboards.choice_kb)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.LIST_OF_ROOMS))
async def get_list_of_rooms(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    await call.message.edit_text(messages.choose_option(), reply_markup=keyboards.my_rooms_kb)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.MY_ROOMS))
async def get_my_admin_rooms(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    rooms = await db.get_my_rooms(call.from_user.id, callback_data.asAdmin)

    kb = await keyboards.rooms_kb(rooms, callback_data.asAdmin)
    await call.message.edit_text(messages.choose_option(), reply_markup=kb)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.SHOW_ROOM))
async def show_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)
    room_name = await get_room_name(callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )
        return

    if callback_data.asAdmin:
        await call.message.edit_text(
            messages.room_admin_title(room_name),
            reply_markup=await keyboards.room_admin_keyboard(callback_data.room_iden),
        )
        return

    if isMemberOrAdmin == "MEMBER NOT EXISTS" or (callback_data.asAdmin == False and isMemberOrAdmin == "IS ADMIN"):
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )
        return

    await call.message.edit_text(
        messages.room_title(room_name),
        reply_markup=await keyboards.room_member_keyboard(callback_data.room_iden),
    )


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.WHO_GIVES))
async def who_gives(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)
    room_name = f'{callback_data.room_iden[:-4]}:{callback_data.room_iden[-4:]}'

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await keyboards.ok_keyboard("None", asAdmin=False),
        )
        return

    status = await db.isStarted(callback_data.room_iden)
    if not status:
        await call.message.edit_text(
            messages.event_not_started(room_name),
            reply_markup=await keyboards.room_member_keyboard(callback_data.room_iden),
        )
        return

    member_id = await db.who_gives(callback_data.room_iden, call.from_user.id)
    if member_id == 'JOINED LATE':
        await call.message.edit_text(
            messages.event_started_before_join(room_name),
            reply_markup=await keyboards.room_member_keyboard(callback_data.room_iden),
        )
        return

    member = await db.get_user(member_id)
    if member:
        user_info = await text.create_user_info(member)
        await call.message.answer(
            messages.gift_target(user_info),
            reply_markup=await keyboards.wishes_keyboard2(callback_data.room_iden, asAdmin=False),
        )

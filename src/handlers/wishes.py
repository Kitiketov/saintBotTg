import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.db import db
from src.keyboards import keyboards
from src.states.states import Gen, CallbackFactory
from src.texts import text

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


@router.callback_query(CallbackFactory.filter(F.action == "my_wishes"))
async def my_wishes(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {await get_room_name(callback_data.room_iden)} не существует",
                                     reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))
        return

    wishes = await db.get_wishes(callback_data.room_iden, call.from_user.id)
    wishes_info = await text.create_wishes_info(wishes)

    await call.message.answer(wishes_info,
                              reply_markup=await keyboards.wishes_keyboard(callback_data.room_iden, asAdmin=False))


@router.callback_query(CallbackFactory.filter(F.action == "edit_wishes"))
async def my_wishes(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {await get_room_name(callback_data.room_iden)} не существует",
                                     reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))
        return

    await state.set_data({'room_iden': callback_data.room_iden})
    await state.set_state(Gen.set_wishes)

    await call.message.answer("Напишите ваше пожелание",
                              reply_markup=await  keyboards.cancel_keyboard("None", asAdmin=False))


@router.message(Gen.set_wishes)
async def edit_wishes_room(msg: Message, state: FSMContext):
    await db.update_user(msg.from_user)
    wishes = msg.text
    data = await state.get_data()
    room_iden = data.get("room_iden")
    await state.clear()

    if msg.text == "🚫Отмена":
        await msg.answer("Меню", reply_markup=keyboards.choice_kb)
        return

    edit_wishes = wishes.replace('\\', '/').replace('\'', '`').replace('\"', '`')
    room_status = await db.edit_wishes(edit_wishes, msg.from_user.id, room_iden)
    if room_status == "ROOM NOT EXISTS":
        await msg.answer("Такой комнаты не существует", reply_markup=await  keyboards.ok_keyboard("None", False))
        return

    if room_status == "MEMBER NOT EXISTS":
        await msg.message.edit_text(f"Вы не участник комнаты", reply_markup=await  keyboards.ok_keyboard("None", False))
        return

    await state.clear()

    await msg.answer(f"Вы изменили пожелание:\n{edit_wishes}",
                     reply_markup=await keyboards.wishes_keyboard(room_iden, asAdmin=False))


@router.callback_query(CallbackFactory.filter(F.action == "see_wishes"))
async def see_wishes(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    isMemberOrAdmin = await db.check_room_and_member(call.from_user.id, callback_data.room_iden)

    if isMemberOrAdmin == "ROOM NOT EXISTS":
        await call.message.edit_text(f"Комнаты {await get_room_name(callback_data.room_iden)} не существует",
                                     reply_markup=await keyboards.ok_keyboard("None", asAdmin=False))
        return

    member_id = await db.who_gives(callback_data.room_iden, call.from_user.id)
    wishes = await db.get_wishes(callback_data.room_iden, member_id)
    wishes_info = await text.take_wishes_info(wishes)

    await call.message.answer(wishes_info, reply_markup=await keyboards.ok_keyboard("None", False))

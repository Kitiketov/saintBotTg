from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.db import db
from src.keyboards import keyboards
from src.states.states import Gen, CallbackFactory


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


@router.callback_query(CallbackFactory.filter(F.action == "join_room"))
async def start_join_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.add_user(call.from_user)
    await state.set_state(Gen.room_name_to_join)
    await call.message.answer("Напишите название комнаты c её id (имякомнаты:id):",
                              reply_markup=await  keyboards.cancel_keyboard("None", False))


@router.message(Gen.room_name_to_join)
async def join_room(msg: Message, state: FSMContext):
    await db.update_user(msg.from_user)
    name = msg.text

    if msg.text == "🚫Отмена":
        await state.clear()
        await msg.answer("Меню", reply_markup=keyboards.choice_kb)
        return

    room_status = await db.connect2room(name, msg.from_user.id)
    if room_status == "room_error":
        await msg.answer("Такой комнаты не существует\nПопробуйте ещё раз:",
                         reply_markup=await  keyboards.cancel_keyboard("None", False))
        return

    elif room_status == "user_error":
        await msg.answer("Вы уже находитесь в этой комнате\n",
                         reply_markup=await keyboards.cancel_keyboard("None", False))
        await state.clear()
        return

    await state.clear()
    kb = await keyboards.room_member_keyboard(f"{''.join(name.split(':'))}")
    await msg.answer(f"{msg.from_user.first_name} вы успешно присоединились к комнате: {name}", reply_markup=kb)

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.db import db
from src.keyboards import keyboards
from src.states.states import Gen, CallbackFactory
from src.texts import messages
from src.texts.callback_actions import CallbackAction


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.JOIN_ROOM))
async def start_join_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.add_user(call.from_user)
    await state.set_state(Gen.room_name_to_join)
    await call.message.answer(
        messages.prompt_join_room(),
        reply_markup=await keyboards.cancel_keyboard("None", False),
    )


@router.message(Gen.room_name_to_join)
async def join_room(msg: Message, state: FSMContext):
    await db.update_user(msg.from_user)
    name = msg.text

    if msg.text == "🚫Отмена":
        await state.clear()
        await msg.answer(messages.menu(), reply_markup=keyboards.choice_kb)
        return

    room_status = await db.connect2room(name, msg.from_user.id)
    if room_status == "room_error":
        await msg.answer(
            messages.room_not_exists_retry(),
            reply_markup=await keyboards.cancel_keyboard("None", False),
        )
        return

    elif room_status == "user_error":
        await msg.answer(
            messages.user_already_in_room(),
            reply_markup=await keyboards.cancel_keyboard("None", False),
        )
        await state.clear()
        return

    await state.clear()
    kb = await keyboards.room_member_keyboard(f"{''.join(name.split(':'))}")
    await msg.answer(
        messages.join_success(msg.from_user.first_name, name),
        reply_markup=kb,
    )

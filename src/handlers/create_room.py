from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.db import db
from src.keyboards import common_kb, room_admin_kb
from src.states.states import Gen, CallbackFactory
from src.texts import messages
from src.texts.callback_actions import CallbackAction

router = Router(name=__name__)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.CREATE_ROOM))
async def start_create_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    room_count = await db.count_user_room(call.from_user.id)

    if room_count > 5:
        await call.message.answer(
            messages.too_many_rooms(),
            reply_markup=await common_kb.cancel_kb("None", False),
        )
        return

    await db.add_user(call.from_user)
    await state.set_state(Gen.room_name_to_create)
    await call.message.answer(messages.prompt_create_room_name(), reply_markup=await common_kb.cancel_kb("None", False))


@router.message(Gen.room_name_to_create)
async def create_room(msg: Message, state: FSMContext):
    await db.update_user(msg.from_user)
    name = msg.text

    if msg.text == "🚫Отмена":
        await state.clear()
        await msg.answer(messages.menu(), reply_markup=common_kb.choice_kb)
        return

    id = await db.create_room(name, msg.from_user.id)
    if not id:
        await msg.answer(
            messages.invalid_room_name(),
            reply_markup=await common_kb.cancel_kb("None", False),
        )
        return

    await state.clear()
    kb = await room_admin_kb.room_admin_kb(f"{name}{id}")
    await msg.answer(
        messages.room_created(name, id),
        reply_markup=kb,
    )

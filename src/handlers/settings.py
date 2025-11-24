from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.db import db
from src.keyboards import common_kb, settings_kb
from src.states.states import CallbackFactory, Gen
from src.texts import messages, settings_texts
from src.texts.callback_actions import CallbackAction
from src.utilities import validators

router = Router(name=__name__)


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


async def check_room_access(user_id, room_iden):
    room_name = await get_room_name(room_iden)
    status = await db.check_room_and_member(user_id, room_iden)
    if status == "ROOM NOT EXISTS":
        return "ROOM NOT EXISTS", room_name

    admin_id = await db.get_room_admin(room_iden)
    if admin_id is None:
        return "ROOM NOT EXISTS", room_name
    if admin_id != user_id:
        return "NOT ADMIN", room_name

    return True, room_name


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.EDIT_ROOM_SETTINGS))
async def show_room_settings(
    call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    await db.update_user(call.from_user)
    access, room_name = await check_room_access(
        call.from_user.id, callback_data.room_iden
    )

    if access == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if access == "NOT ADMIN":
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    _, price, event_time, exchange_type = await db.get_room_settings(
        callback_data.room_iden
    )
    info = settings_texts.room_settings_info(
        room_name, price, event_time, exchange_type
    )
    kb = await settings_kb.settings_view_kb(
        callback_data.room_iden, callback_data.asAdmin
    )
    await call.message.answer(info, reply_markup=kb)


@router.callback_query(
    CallbackFactory.filter(F.action == CallbackAction.SHOW_ROOM_SETTINGS)
)
async def show_room_settings_member(
    call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    await db.update_user(call.from_user)
    status = await db.check_room_and_member(
        call.from_user.id, callback_data.room_iden
    )
    room_name = await get_room_name(callback_data.room_iden)

    if status == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if status == "MEMBER NOT EXISTS":
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    _, price, event_time, exchange_type = await db.get_room_settings(
        callback_data.room_iden
    )
    info = settings_texts.room_settings_info(
        room_name, price, event_time, exchange_type
    )
    kb = await settings_kb.settings_view_kb(
        callback_data.room_iden, callback_data.asAdmin
    )
    await call.message.answer(info, reply_markup=kb)


@router.callback_query(
    CallbackFactory.filter(F.action == CallbackAction.OPEN_ROOM_SETTINGS_EDIT)
)
async def open_settings_edit(
    call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    await db.update_user(call.from_user)
    access, room_name = await check_room_access(
        call.from_user.id, callback_data.room_iden
    )

    if access == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if access == "NOT ADMIN":
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    _, price, event_time, exchange_type = await db.get_room_settings(
        callback_data.room_iden
    )
    info = settings_texts.room_settings_info(
        room_name, price, event_time, exchange_type
    )
    kb = await settings_kb.settings_edit_kb(
        callback_data.room_iden, callback_data.asAdmin
    )
    await call.message.edit_text(info, reply_markup=kb)


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.EDIT_ROOM_PRICE))
async def edit_room_price(
    call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    await db.update_user(call.from_user)
    access, room_name = await check_room_access(
        call.from_user.id, callback_data.room_iden
    )

    if access == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if access == "NOT ADMIN":
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    await state.set_state(Gen.set_room_price)
    await state.set_data({"room_iden": callback_data.room_iden})

    _, price, *_ = await db.get_room_settings(callback_data.room_iden)
    await call.message.answer(
        settings_texts.prompt_price(price),
        reply_markup=await common_kb.cancel_kb("None", asAdmin=True),
    )


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.EDIT_ROOM_TIME))
async def edit_room_time(
    call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    await db.update_user(call.from_user)
    access, room_name = await check_room_access(
        call.from_user.id, callback_data.room_iden
    )

    if access == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if access == "NOT ADMIN":
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    await state.set_state(Gen.set_room_time)
    await state.set_data({"room_iden": callback_data.room_iden})

    _, _, event_time, _ = await db.get_room_settings(callback_data.room_iden)
    await call.message.answer(
        settings_texts.prompt_event_time(event_time),
        reply_markup=await common_kb.cancel_kb("None", asAdmin=True),
    )


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.EDIT_ROOM_TYPE))
async def edit_room_type(
    call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    await db.update_user(call.from_user)
    access, room_name = await check_room_access(
        call.from_user.id, callback_data.room_iden
    )

    if access == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if access == "NOT ADMIN":
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    _, _, _, exchange_type = await db.get_room_settings(callback_data.room_iden)
    await call.message.edit_text(
        settings_texts.choose_exchange_type(exchange_type),
        reply_markup=await settings_kb.settings_type_kb(
            callback_data.room_iden, callback_data.asAdmin
        ),
    )


@router.callback_query(
    CallbackFactory.filter(
        F.action.in_(
            [CallbackAction.SET_ROOM_TYPE_CENTRAL, CallbackAction.SET_ROOM_TYPE_THROW]
        )
    )
)
async def set_room_type(
    call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    await db.update_user(call.from_user)
    access, room_name = await check_room_access(
        call.from_user.id, callback_data.room_iden
    )

    if access == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    if access == "NOT ADMIN":
        await call.message.edit_text(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    new_type = (
        "централизованый"
        if callback_data.action == CallbackAction.SET_ROOM_TYPE_CENTRAL
        else "подброс подарка"
    )
    status = await db.update_room_settings(
        callback_data.room_iden, exchange_type=new_type
    )
    if status == "ROOM NOT EXISTS":
        await call.message.edit_text(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    _, price, event_time, exchange_type = await db.get_room_settings(
        callback_data.room_iden
    )
    info = settings_texts.settings_updated(
        room_name, price, event_time, exchange_type
    )
    kb = await settings_kb.settings_view_kb(
        callback_data.room_iden, callback_data.asAdmin
    )
    await call.message.edit_text(info, reply_markup=kb)


@router.message(Gen.set_room_price)
async def set_room_price(msg: Message, state: FSMContext):
    await db.update_user(msg.from_user)
    data = await state.get_data()
    room_iden = data.get("room_iden")

    if msg.text == "🚫Отмена":
        await state.clear()
        if room_iden:
            _, price, event_time, exchange_type = await db.get_room_settings(room_iden)
            room_name = await get_room_name(room_iden)
            await msg.answer(
                settings_texts.room_settings_info(
                    room_name, price, event_time, exchange_type
                ),
                reply_markup=await settings_kb.settings_view_kb(room_iden, True),
            )
        else:
            await msg.answer(messages.menu(), reply_markup=common_kb.choice_kb)
        return

    if not room_iden:
        await state.clear()
        await msg.answer(messages.menu(), reply_markup=common_kb.choice_kb)
        return

    price = validators.normalize_price_range(msg.text)
    if not price:
        await msg.answer(
            settings_texts.invalid_price(),
            reply_markup=await common_kb.cancel_kb("None", asAdmin=True),
        )
        return

    access, room_name = await check_room_access(msg.from_user.id, room_iden)
    if access == "ROOM NOT EXISTS":
        await state.clear()
        await msg.answer(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return
    if access == "NOT ADMIN":
        await state.clear()
        await msg.answer(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    await db.update_room_settings(room_iden, price=price)
    _, new_price, event_time, exchange_type = await db.get_room_settings(room_iden)
    await state.clear()
    await msg.answer(
        settings_texts.settings_updated(
            room_name, new_price, event_time, exchange_type
        ),
        reply_markup=await settings_kb.settings_view_kb(room_iden, True),
    )


@router.message(Gen.set_room_time)
async def set_room_time(msg: Message, state: FSMContext):
    await db.update_user(msg.from_user)
    data = await state.get_data()
    room_iden = data.get("room_iden")

    if msg.text == "🚫Отмена":
        await state.clear()
        if room_iden:
            _, price, event_time, exchange_type = await db.get_room_settings(room_iden)
            room_name = await get_room_name(room_iden)
            await msg.answer(
                settings_texts.room_settings_info(
                    room_name, price, event_time, exchange_type
                ),
                reply_markup=await settings_kb.settings_view_kb(room_iden, True),
            )
        else:
            await msg.answer(messages.menu(), reply_markup=common_kb.choice_kb)
        return

    if not room_iden:
        await state.clear()
        await msg.answer(messages.menu(), reply_markup=common_kb.choice_kb)
        return

    event_time = validators.normalize_event_time(msg.text)
    if not event_time:
        await msg.answer(
            settings_texts.invalid_event_time(),
            reply_markup=await common_kb.cancel_kb("None", asAdmin=True),
        )
        return

    access, room_name = await check_room_access(msg.from_user.id, room_iden)
    if access == "ROOM NOT EXISTS":
        await state.clear()
        await msg.answer(
            messages.room_not_exists(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return
    if access == "NOT ADMIN":
        await state.clear()
        await msg.answer(
            messages.not_a_member(room_name),
            reply_markup=await common_kb.ok_kb("None", asAdmin=False),
        )
        return

    await db.update_room_settings(room_iden, event_time=event_time)
    _, price, new_event_time, exchange_type = await db.get_room_settings(room_iden)
    await state.clear()
    await msg.answer(
        settings_texts.settings_updated(
            room_name, price, new_event_time, exchange_type
        ),
        reply_markup=await settings_kb.settings_view_kb(room_iden, True),
    )

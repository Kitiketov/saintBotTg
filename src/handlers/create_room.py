from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.db import db
from src.keyboards import keyboards
from src.states.states import Gen, CallbackFactory

router = Router(name=__name__)


@router.callback_query(CallbackFactory.filter(F.action == "create_room"))
async def start_create_room(call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await db.update_user(call.from_user)
    room_count = await db.count_user_room(call.from_user.id)

    if room_count > 5:
        await call.message.answer("Превышено количество созданных вами комнат\n",
                                  reply_markup=await keyboards.cancel_keyboard("None", False))
        return

    await db.add_user(call.from_user)
    await state.set_state(Gen.room_name_to_create)
    await call.message.answer("Введите название комнаты:", reply_markup=await keyboards.cancel_keyboard("None", False))


@router.message(Gen.room_name_to_create)
async def create_room(msg: Message, state: FSMContext):
    await db.update_user(msg.from_user)
    name = msg.text

    if msg.text == "🚫Отмена":
        await state.clear()
        await msg.answer("Меню", reply_markup=keyboards.choice_kb)
        return

    id = await db.create_room(name, msg.from_user.id)
    if not id:
        await msg.answer(
            "Имя не должно содержать _mem , _saint, символы кроме  _ , цифры в начале , пробелы и не длинее 30 символов\nПридумайте другое название:",
            reply_markup=await keyboards.cancel_keyboard("None", False))
        return

    await state.clear()
    kb = await keyboards.room_admin_keyboard(f"{name}{id}")
    await msg.answer(
        f"Комната:  {name}:{id} создана \nЧтобы другие могли в неё войти скажите им её название c id\n<b>Админ автоматически не является участником</b>",
        reply_markup=kb)

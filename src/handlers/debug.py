from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.texts import messages


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


@router.message(Command("ID"))
async def get_id(msg: Message):
    forwarder_id = msg.from_user.id

    if msg.forward_from:
        original_user_id = msg.forward_from.id
        await msg.answer(
            f"Твой id: {forwarder_id}\n"
            f"ID оригинального отправителя: {original_user_id}"
        )
        return

    if msg.forward_from_chat:
        chat_id = msg.forward_from_chat.id
        await msg.answer(
            f"Твой id: {forwarder_id}\n"
            f"ID канала/чата: {chat_id}"
        )
        print(1)
        await msg.bot.send_message(chat_id=chat_id, text='Привет!',)
        return

    await msg.answer(
        "Не могу получить ID оригинального отправителя — "
        "скорее всего, у него включена приватность пересылок."
    )
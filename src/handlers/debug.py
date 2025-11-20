from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


@router.message(Command("ID"))
async def get_id(msg: Message):
    await msg.answer(f"ID: user_id - {msg.from_user.id}\n      chat_id - {msg.chat.id}")

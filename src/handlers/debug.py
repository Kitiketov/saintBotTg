from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.texts import messages


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


@router.message(Command("ID"))
async def get_id(msg: Message):
    await msg.answer(messages.id_info(msg.from_user.id, msg.chat.id))

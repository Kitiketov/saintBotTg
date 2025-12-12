from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.texts import messages


router = Router(name=__name__)


@router.message(Command("info"))
async def say_about_santa(msg: Message):
    await msg.answer(messages.about_santa())

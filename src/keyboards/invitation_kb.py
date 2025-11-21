import base64

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def join_to_room_kb(room_iden: str,bot_name: str):
    room_iden64 = base64.urlsafe_b64encode(room_iden.encode()).decode().replace("=", "")
    join_kb = [
        [
            InlineKeyboardButton(
                text="Я участвую",
                url=f"https://t.me/{bot_name}?start=join_to_room-{room_iden64}end_invitation",
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=join_kb)

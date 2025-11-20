from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.states import states
from src.texts.callback_actions import CallbackAction


my_rooms_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Комнаты где я участник",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.MY_ROOMS, room_iden="None", asAdmin=False
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Комнаты где я админ",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.MY_ROOMS, room_iden="None", asAdmin=True
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️Вернуться в меню",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.BACK_TO_MENU, room_iden="None", asAdmin=False
                ).pack(),
            )
        ],
    ]
)


async def rooms_kb(rooms_idens, asAdmin):
    builder = InlineKeyboardBuilder()
    for room_iden in rooms_idens:
        builder.button(
            text=f"{room_iden[:-4]}:{room_iden[-4:]}",
            callback_data=states.CallbackFactory(
                action=CallbackAction.SHOW_ROOM, room_iden=room_iden, asAdmin=asAdmin
            ).pack(),
        )
        builder.adjust(1)
    builder.button(
        text="◀️Вернуться в меню",
        callback_data=states.CallbackFactory(
            action=CallbackAction.BACK_TO_MENU, room_iden="None", asAdmin=False
        ).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()

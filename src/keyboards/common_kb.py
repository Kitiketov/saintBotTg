from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.states import states
from src.texts.callback_actions import CallbackAction


choice_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❇Создать комнату",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.CREATE_ROOM, room_iden="None", asAdmin=False
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="✴Присоединиться к существующей",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.JOIN_ROOM, room_iden="None", asAdmin=False
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹСтатус ваших групп",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.LIST_OF_ROOMS, room_iden="None", asAdmin=False
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="🚫Закрыть окно",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.CANCEL, room_iden=" ", asAdmin=False
                ).pack(),
            )
        ],
    ]
)


async def cancel_kb(room_iden, asAdmin):
    cancel_kb = [
        [
            InlineKeyboardButton(
                text="🚫Отмена",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.CANCEL, room_iden=room_iden, asAdmin=asAdmin
                ).pack(),
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=cancel_kb)


async def ok_kb(room_iden, asAdmin):
    ok_kb = [
        [
            InlineKeyboardButton(
                text="✅OK",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.CANCEL, room_iden=room_iden, asAdmin=asAdmin
                ).pack(),
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=ok_kb)

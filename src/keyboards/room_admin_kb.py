from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.states import states
from src.texts.callback_actions import CallbackAction


async def room_admin_kb(room_iden):
    room_kb = [
        [
            InlineKeyboardButton(
                text="🎲Начать событие",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.START_EVENT, room_iden=room_iden, asAdmin=True
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="📄Список участников",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.MEMBERS_LIST,
                    room_iden=room_iden,
                    asAdmin=True,
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="✏️Изменить настройки комнаты",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.EDIT_ROOM_SETTINGS,
                    room_iden=room_iden,
                    asAdmin=True,
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="❌Удалить комнату",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.DELETE_ROOM, room_iden=room_iden, asAdmin=True
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="📛Удалить участника",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.REMOVE_MEMBER,
                    room_iden=room_iden,
                    asAdmin=True,
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="✉️Создать приглашение",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.CREATE_INVITATION,
                    room_iden=room_iden,
                    asAdmin=True,
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️Вернуться в меню",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.BACK_TO_MENU,
                    room_iden=room_iden,
                    asAdmin=True,
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="🚫Закрыть окно",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.CANCEL, room_iden=room_iden, asAdmin=True
                ).pack(),
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=room_kb)


async def confirm_kb(room_iden, asAdmin):
    confirm_kb = [
        [
            InlineKeyboardButton(
                text="✅Да",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.CONFIRM_DELETE,
                    room_iden=room_iden,
                    asAdmin=asAdmin,
                ).pack(),
            ),
            InlineKeyboardButton(
                text="🚫Нет",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.CANCEL, room_iden=room_iden, asAdmin=asAdmin
                ).pack(),
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=confirm_kb)


async def member_kb(members, room_iden):
    builder = InlineKeyboardBuilder()
    for member in members:
        builder.button(
            text=f"{member[1]} {member[2]}",
            callback_data=states.RemoveCallbackFactory(
                action=CallbackAction.REMOVE_MEMBER,
                room_iden=room_iden,
                user_id=member[0],
            ).pack(),
        )
        builder.adjust(1)
    builder.button(
        text="🚫Отмена",
        callback_data=states.CallbackFactory(
            action=CallbackAction.CANCEL, room_iden=room_iden, asAdmin=True
        ).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


async def refresh_list_kb(room_iden, asAdmin):
    refresh_list_kb = [
        [
            InlineKeyboardButton(
                text="🔄Обновить",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.REFRESH_LIST,
                    room_iden=room_iden,
                    asAdmin=False,
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="🚫Отмена",
                callback_data=states.CallbackFactory(
                    action=CallbackAction.CANCEL, room_iden=room_iden, asAdmin=False
                ).pack(),
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=refresh_list_kb)

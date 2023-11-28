from aiogram.types import ReplyKeyboardMarkup, KeyboardButton ,InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import states

choice_kb = [
    [InlineKeyboardButton(text="❇Создать комнату", callback_data=states.CallbackFactory(action="create_room",room_iden='None',asAdmin=False).pack())],
    [InlineKeyboardButton(text="✴Присоединиться к существующей", callback_data=states.CallbackFactory(action="join_room",room_iden='None',asAdmin=False).pack())],
    [InlineKeyboardButton(text="ℹСтатус ваших групп", callback_data=states.CallbackFactory(action="list_of_rooms",room_iden='None',asAdmin=False).pack())]
]

async def room_admin_keyboard(room_iden):
    room_kb = [
        [InlineKeyboardButton(text="🎲Начать событие", callback_data=states.CallbackFactory(action="start_event",room_iden=room_iden,asAdmin=True).pack())],
        [InlineKeyboardButton(text="📄Список участников", callback_data=states.CallbackFactory(action="members_list",room_iden=room_iden,asAdmin=True).pack())],
        [InlineKeyboardButton(text="✏️Изменить настройки комнаты", callback_data=states.CallbackFactory(action="edit_room_settings",room_iden=room_iden,asAdmin=True).pack())],
        [InlineKeyboardButton(text="❌Удалить комнату" , callback_data=states.CallbackFactory(action="delete_room",room_iden=room_iden,asAdmin=True).pack())],
        [InlineKeyboardButton(text="📛Удалить участника", callback_data=states.CallbackFactory(action="remove_member",room_iden=room_iden,asAdmin=True).pack())],
        [InlineKeyboardButton(text="◀️Вернуться в меню", callback_data=states.CallbackFactory(action="back_to_menu",room_iden=room_iden,asAdmin=True).pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=room_kb) 

async def room_member_keyboard(room_iden):
    room_join_kb = [
        [InlineKeyboardButton(text="🎁Кому я дарю",callback_data=states.CallbackFactory(action="who_gives",room_iden=room_iden,asAdmin=False).pack())],
        [InlineKeyboardButton(text="📄Список участников",callback_data=states.CallbackFactory(action="members_list",room_iden=room_iden,asAdmin=False).pack())],
        [InlineKeyboardButton(text="🚪Покинуть комнату",callback_data=states.CallbackFactory(action="leave_room",room_iden=room_iden,asAdmin=False).pack())],
        [InlineKeyboardButton(text="◀️Вернуться в меню",callback_data=states.CallbackFactory(action="back_to_menu",room_iden=room_iden,asAdmin=False).pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=room_join_kb)
async def cancel_keyboard(room_iden,asAdmin):
    cancel_kb = [
        [InlineKeyboardButton(text="🚫Отмена",callback_data=states.CallbackFactory(action="cancel",room_iden=room_iden,asAdmin=asAdmin).pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=cancel_kb)
async def ok_keyboard(room_iden,asAdmin):
    cancel_kb = [
        [InlineKeyboardButton(text="✅OK",callback_data=states.CallbackFactory(action="cancel",room_iden=room_iden,asAdmin=asAdmin).pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=cancel_kb)
my_rooms_kb = [
    [InlineKeyboardButton(text="Комнаты где я участник",callback_data=states.CallbackFactory(action="my_rooms",room_iden="None",asAdmin=False).pack())],
    [InlineKeyboardButton(text="Комнаты где я админ",callback_data=states.CallbackFactory(action="my_rooms",room_iden="None",asAdmin=True).pack())],
    [InlineKeyboardButton(text="◀️Вернуться в меню", callback_data=states.CallbackFactory(action="back_to_menu",room_iden="None",asAdmin=False).pack())]
]

async def rooms_kb(rooms_idens,asAdmin):
    builder = InlineKeyboardBuilder()
    for room_iden in rooms_idens:
        builder.button(text=f"{room_iden[:-4]}:{room_iden[-4:]}",callback_data=states.CallbackFactory(action="show_room",room_iden=room_iden,asAdmin=asAdmin).pack())
        builder.adjust(1)
    builder.button(text="◀️Вернуться в меню", callback_data=states.CallbackFactory(action="back_to_menu",room_iden="None",asAdmin=False).pack())
    builder.adjust(1)
    return builder.as_markup()

async def member_keyboard(members,room_iden):
    builder = InlineKeyboardBuilder()
    for member in members:
        builder.button(text=f"{member[1]} {member[2]}",callback_data=states.RemoveCallbackFactory(action="remove_member",room_iden=room_iden,user_id=member[0]).pack())
        builder.adjust(1)
    builder.button(text="🚫Отмена",callback_data=states.CallbackFactory(action="cancel",room_iden=room_iden,asAdmin=True).pack())
    builder.adjust(1)
    return builder.as_markup()

my_rooms_kb = InlineKeyboardMarkup(inline_keyboard=my_rooms_kb)
choice_kb = InlineKeyboardMarkup(inline_keyboard=choice_kb)

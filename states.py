from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData


class CallbackFactory(CallbackData, prefix="calldata"):
    action: str
    room_iden : str = ''
    asAdmin : bool

class RemoveCallbackFactory(CallbackData, prefix="remem"):
    action: str
    room_iden : str = ''
    user_id : int

class Gen(StatesGroup):
    room_name_to_create = State()
    room_name_to_join= State()
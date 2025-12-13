from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReactionTypeEmoji

from src.keyboards import common_kb
from src.states.states import CallbackFactory
from src.texts import messages
from src.texts.callback_actions import CallbackAction

EFFECT_IDS = {
    '🔥': "5104841245755180586",
    '👍': "5107584321108051014",
    '👎': "5104858069142078462",
    '❤️': "5044134455711629726",
    '🎉': "5046509860389126442",
    '💩': "5046589136895476101"
}


async def set_reaction(message: Message) -> None:
    """
    Устанавливает реакцию 👍 на сообщение пользователя.

    Args:
        message (Message): Объект сообщения от пользователя.
    """
    await message.bot.set_message_reaction(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reaction=[ReactionTypeEmoji(emoji="👍")],
    )


async def get_room_name(room_iden):
    return f"{room_iden[:-4]}:{room_iden[-4:]}"


router = Router(name=__name__)


async def _delete_message_if_exists(message: Message) -> None:
    if not message:
        return

    try:
        await message.delete()
    except TelegramBadRequest as exc:
        if "message to delete not found" not in exc.message.lower():
            raise


@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.CANCEL))
async def cancel(
        call: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
):
    if callback_data.room_iden == "None":
        await state.clear()
    await _delete_message_if_exists(call.message)


@router.message(F.text == "◀️Вернуться в меню")
@router.callback_query(CallbackFactory.filter(F.action == CallbackAction.BACK_TO_MENU))
async def menu(call: CallbackQuery, callback_data: CallbackFactory):
    await call.message.edit_text(messages.menu(), reply_markup=common_kb.choice_kb)

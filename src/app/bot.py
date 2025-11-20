from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.handlers import (
    legacy_route,
    common,
    create_room,
    room_admin,
    wishes,
invitation
)


async def run_bot(token: str) -> None:
    bot = Bot(token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        legacy_route.router,
        common.router,
        wishes.router,
        room_admin.router,
        create_room.router,
        invitation.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

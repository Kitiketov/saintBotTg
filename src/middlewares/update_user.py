from aiogram import BaseMiddleware

from src.db import db


class UpdateUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if user:
            await db.update_user(user)
        return await handler(event, data)

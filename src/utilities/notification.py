import asyncio
from functools import wraps
from typing import AsyncGenerator

from aiogram.exceptions import TelegramRetryAfter

from src.config import logger


def safe_send(max_retries: int = 1):
    def deco(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return await fn(*args, **kwargs)
                except TelegramRetryAfter as e:
                    attempt += 1
                    if attempt > max_retries:
                        logger.warning("RetryAfter maxed: %s", e)
                        return None
                    await asyncio.sleep(e.retry_after)
                except Exception as e:
                    logger.warning("Send failed: %s", e)
                    return None

        return wrapper

    return deco

@safe_send(max_retries=1)
async def notify_user(bot, user_id: int, text: str, reply_markup=None, message_effect_id=None):
    return await bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=reply_markup,
        message_effect_id=message_effect_id,
    )
async def broadcast(bot, user_ids: list[int], text: str, reply_markup=None, message_effect_id=None, delay: float = 0.05):
    for uid in user_ids:
        await notify_user(bot, uid, text, reply_markup=reply_markup, message_effect_id=message_effect_id)
        await asyncio.sleep(delay)
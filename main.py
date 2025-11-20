import asyncio

from src.app.bot import run_bot
from src.config import settings


async def main() -> None:
    await run_bot(settings.bot_token)


if __name__ == "__main__":
    asyncio.run(main())

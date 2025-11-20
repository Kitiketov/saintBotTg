import asyncio

from src.config import settings
from src.app.bot import run_bot


async def main() -> None:
    await run_bot(settings.bot_token)


if __name__ == "__main__":
    asyncio.run(main())

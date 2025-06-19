import logging

from config.logging_config import logging_configure

logging_configure(level=logging.DEBUG, filemode="w")

import asyncio

from app import bot


async def main():
    await bot.main()


asyncio.run(main())

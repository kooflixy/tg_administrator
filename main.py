import logging

from config.logging_config import logging_configure

logging_configure(level=logging.INFO, filemode="a")

import asyncio

from app import bot
from app.handlers.distribution import distribution


async def main():
    aiogram_task = asyncio.create_task(bot.main())
    distribution_task = asyncio.create_task(distribution())

    await asyncio.gather(distribution_task, aiogram_task)


asyncio.run(main())

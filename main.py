import logging
from config.logging_config import logging_configure

logging_configure(level=logging.INFO, filemode='w')

from app import bot
import asyncio

async def main():
    await bot.main()

asyncio.run(main())
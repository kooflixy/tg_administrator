from app import bot
import asyncio
import logging

logging.getLogger("aiogram.event").setLevel(logging.WARNING) # логи aiogram только с logging.WARNING

stream_formatter = logging.Formatter("%(asctime)s %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(stream_formatter)
logging.basicConfig(level=logging.INFO, encoding='utf-8', handlers=[stream_handler])

async def main():
    await bot.main()

asyncio.run(main())
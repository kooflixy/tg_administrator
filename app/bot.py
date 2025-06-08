from aiogram import Dispatcher

from app.bot_obj import bot
from app.handlers import user_commands, settings


async def main():
    dp = Dispatcher()
    dp.include_routers(
        user_commands.router,
        settings.chat_list.router
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
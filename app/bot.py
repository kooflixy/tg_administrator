from aiogram import Dispatcher

from app.bot_obj import bot
from app.handlers import user_commands, delete_sys_messages, captcha, settings, pagination


async def main():
    dp = Dispatcher()
    dp.include_routers(
        user_commands.router,
        delete_sys_messages.router, 
        captcha.router,

        pagination.router,

        settings.chat_settings.chat.router,
        settings.chat_settings.adding_chat.router,

        settings.moderator_settings.moderator.router,
        settings.moderator_settings.adding_moderator.router,
        settings.moderator_settings.moderator_chat.router,
        settings.moderator_settings.adding_moderator_chat.router,

        settings.captcha.router,
    )
    await bot.delete_webhook(drop_pending_updates=True)
    print('start')
    await dp.start_polling(bot)
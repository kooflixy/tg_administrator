from aiogram import Dispatcher
from aiogram.types import ErrorEvent

from app.bot_obj import bot
from app.handlers import delete_sys_message, user_commands, captcha, settings, pagination, error, administration


async def main():
    dp = Dispatcher()

    dp.include_routers(
        user_commands.router,
        delete_sys_message.router, 
        captcha.router,

        pagination.router,

        settings.chat_settings.chat.router,
        settings.chat_settings.adding_chat.router,

        settings.moderator_settings.moderator.router,
        settings.moderator_settings.adding_moderator.router,
        settings.moderator_settings.moderator_chat.router,
        settings.moderator_settings.adding_moderator_chat.router,

        administration.ban.router,
        administration.kick.router,
        administration.mute.router,
        administration.warn.router,

        settings.captcha.router,

        error.router
    )
    await bot.delete_webhook(drop_pending_updates=True)
    print('start')
    await dp.start_polling(bot)
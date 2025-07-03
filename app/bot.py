from aiogram import Dispatcher
from aiogram.types import ErrorEvent

from app.bot_obj import bot
from app.handlers import (
    administration,
    captcha,
    delete_sys_message,
    error,
    pagination,
    settings,
    user_commands,
)


async def main():
    dp = Dispatcher()

    # fmt: off
    dp.include_routers(
        user_commands.router,

        delete_sys_message.router,

        captcha.router,

        pagination.router,

        settings.set_text.router,
        settings.linkto.router,
        settings.captcha.router,
        settings.warn.router,

        settings.distribution_settings.distribution.router,
        settings.distribution_settings.adding_distribution.router,
        settings.distribution_settings.distribution_chat.router,
        settings.distribution_settings.adding_distribution_chat.router,

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
        administration.list.router,
        administration.close.router,
        administration.linkto.router,

        error.router,
    )
    # fmt: on

    await bot.delete_webhook(drop_pending_updates=True)
    print("start")
    await dp.start_polling(bot)

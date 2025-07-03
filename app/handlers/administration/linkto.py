from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot_obj import bot
from app.utils.checkers import RestChecker
from app.utils.contrib import get_msg_url_reason
from app.utils.for_logging import name_in_log
from app.utils.rest_handler import LinktoRestHandler
from app.utils.text_markup import TextMarkup
from config import changeable_settings
from db.queries.chat_orm import ChatORMHandler

log = getLogger(__name__)

router = Router()


@router.message(Command("linkto"))
async def linkto(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await LinktoRestHandler.is_perm_exists(
        message.from_user.id, message.chat.id
    ):
        return

    log.info(
        "Попытка переслать сообщение moderator=%s",
        name_in_log.user(message),
    )

    if not changeable_settings.linkto_chat_id:
        await RestChecker.reply_n_delete("Чат для линковки не привязан", message)
        return

    msg_url, reason = get_msg_url_reason(message, command)

    if not await RestChecker.is_linkto_data_valid(msg_url, reason, message):
        return

    try:
        await bot.send_message(
            changeable_settings.linkto_chat_id,
            text=f"""
    👤Модер: {TextMarkup.tag_user(message.from_user.full_name, message.from_user.id)}{f"\n👁Причина: {reason}" if reason else ''}
💬Сообщение: {msg_url}""",
        )

        log.info(
            "Переслано сообщение moderator=%s msg_url=%s reason=%r",
            name_in_log.user(message),
            msg_url,
            reason,
        )
    except:
        log.exception(
            "При попытке переслать сообщение произошла ошибкаmoderator=%s msg_url=%s reason=%r",
            name_in_log.user(message),
            msg_url,
            reason,
        )

    await RestChecker.reply_n_delete("Успешно переслано", message)

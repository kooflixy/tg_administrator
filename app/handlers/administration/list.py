from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot_obj import bot
from app.contrib.checkers import RestChecker
from app.contrib.telthon_manager import TelethonManager
from app.contrib.text_markup import TextMarkup
from app.utils.rest_handler.ban_rest import BanRestHandler
from db.queries.chat_orm import ChatORMHandler

log = getLogger(__name__)

router = Router()

DELETE_TIME = 240


@router.message(Command("banlist"))
async def get_ban_list(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)

    # Проверка, является ли пользователь модератором чата
    if not await RestChecker.is_user_moderator(
        chat_member, message, send_message=False
    ):
        return

    log.info(
        "Попытка получить список банов moderator=%s chat_id=%s",
        message,
        message.chat.id,
    )

    banned_users_list = await BanRestHandler.get_chat_all(message.chat.id)
    if banned_users_list:
        text_list = []
        for banned_user in banned_users_list:
            user = await TelethonManager.get_user(banned_user.user_id)
            if not user:
                continue
            moderator = await TelethonManager.get_user(banned_user.by_moderator_id)

            user_str = TextMarkup.tag_user(TelethonManager.get_full_name(user), user.id)
            moderator_str = (
                TextMarkup.tag_user(
                    TelethonManager.get_full_name(moderator), moderator.id
                )
                if moderator
                else "<b><i>модератор удален<i></b>"
            )

            user_text = f"🚫 {user_str} был забанен модератором {moderator_str}\n  Дата: {banned_user.created_at.strftime('%Y-%m-%d %H:%M')}"
            text_list.append(user_text)

            text = "\n\n".join(text_list)
    else:
        text = "Забаненных пользователей нет:)"

    log.info("Получен список банов moderator=%s chat_id=%s", message, message.chat.id)

    await RestChecker.reply_n_delete(text, message, DELETE_TIME)

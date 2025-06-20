from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot_obj import bot
from app.contrib.checkers import RestChecker
from app.contrib.for_logging import name_in_log
from app.contrib.text_markup import TextMarkup
from app.utils.contrib import get_user_id_name
from app.utils.rest_handler import KickRestHandler
from db.queries.chat_orm import ChatORMHandler

log = getLogger(__name__)

router = Router()


@router.message(Command("kick"))
async def mute_user(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await KickRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    log.debug(
        "%s решил забанить пользователя user_id=%r chat_id=%s",
        name_in_log.user(message),
        command.args,
        message.chat.id,
    )

    # Получение пользователя
    user = await get_user_id_name(message, command)

    # Проверка на существование пользователя
    if not await RestChecker.is_user_exists(user, message):
        return

    # Проверка, является ли пользователь текущим ботом
    if await RestChecker.is_user_main_bot(user.id, message):
        return

    chat_member = await bot.get_chat_member(message.chat.id, user.id)

    # Проверка, является ли пользователь участником группы
    if not await RestChecker.is_user_member(chat_member, message):
        return

    # Проверка, является ли пользователь модератором чата
    if await RestChecker.is_user_moderator(chat_member, message):
        return

    await bot.ban_chat_member(message.chat.id, user.id)
    await bot.unban_chat_member(message.chat.id, user.id)

    await RestChecker.reply_n_delete(
        f"{TextMarkup.tag_user(user.name, user.id)} успешно кикнут", message
    )

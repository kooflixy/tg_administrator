import asyncio
from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatMemberBanned, Message

from app.bot_obj import bot
from app.contrib.checkers import RestChecker
from app.contrib.for_logging import name_in_log
from app.contrib.telthon_manager import TelethonManager
from app.contrib.text_markup import TextMarkup
from app.utils.contrib import get_user_id_name
from app.utils.rest_handler import BanRestHandler
from db.database import async_session_factory
from db.queries import ChatORMHandler, ModeratorChatORMHandler

log = getLogger(__name__)

router = Router()


@router.message(Command("ban"))
async def ban_user(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await BanRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

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

    log.info(
        "Попытка забанить moderator=%s user=%r chat_id=%s",
        name_in_log.user(message),
        user,
        message.chat.id,
    )

    async with async_session_factory() as session:
        rest = await BanRestHandler.apply_restriction(
            session,
            moderator_id=message.from_user.id,
            chat_id=message.chat.id,
            user_id=user.id,
        )

        if rest:
            await bot.ban_chat_member(message.chat.id, user.id)
            await session.commit()
            log.info(
                "Пользователь забанен moderator=%s user=%r chat_id=%s",
                name_in_log.user(message),
                user,
                message.chat.id,
            )

            await RestChecker.reply_n_delete(
                f"{TextMarkup.tag_user(user.name, user.id)} забанен навсегда(", message
            )
        else:
            log.info(
                "Попытка забанить уже забаненного moderator=%s user=%r chat_id=%s",
                name_in_log.user(message),
                user,
                message.chat.id,
            )
            await RestChecker.reply_n_delete(
                f"{TextMarkup.tag_user(user.name, user.id)} уже находится в бане",
                message,
            )


@router.message(Command("unban"))
async def unban_user(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await BanRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    user = await get_user_id_name(message, command)

    # Проверка на существование пользователя
    if not await RestChecker.is_user_exists(user, message):
        return

    log.info(
        "Попытка разбанить moderator=%s user=%r chat_id=%s",
        name_in_log.user(message),
        user,
        message.chat.id,
    )

    async with async_session_factory() as session:
        # удаление бана из бд
        await BanRestHandler.remove(session, chat_id=message.chat.id, user_id=user.id)

        # Проверка, является ли пользователь забаненным. Если да, то разбан
        if isinstance(
            await bot.get_chat_member(message.chat.id, user.id), ChatMemberBanned
        ):
            await bot.unban_chat_member(message.chat.id, user.id)
            await session.commit()
            log.info(
                "Пользователь забанен moderator=%s user=%r chat_id=%s",
                name_in_log.user(message),
                user,
                message.chat.id,
            )

            await RestChecker.reply_n_delete(
                f"{TextMarkup.tag_user(user.name, user.id)} успешно разбанен", message
            )
        else:
            await session.commit()

            log.info(
                "Попытка разбанить незабаненного moderator=%s user=%r chat_id=%s",
                name_in_log.user(message),
                user,
                message.chat.id,
            )
            await RestChecker.reply_n_delete(
                f"{TextMarkup.tag_user(user.name, user.id)} не забанен", message
            )

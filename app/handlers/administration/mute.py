from datetime import datetime, timedelta, timezone
from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatPermissions, Message

from app.bot_obj import bot
from app.utils.checkers import RestChecker
from app.utils.contrib import (
    MUTE_FOREVER,
    get_user_id_name,
    get_user_id_name_period,
)
from app.utils.for_logging import name_in_log
from app.utils.perm import permissions_to_dict
from app.utils.rest_handler import MuteRestHandler
from app.utils.rest_handler.ban_rest import BanRestHandler
from app.utils.rest_handler.perm_rest import PermRestHandler
from app.utils.text_markup import TextMarkup
from app.utils.time import get_local_time
from db.database import async_session_factory
from db.queries.chat_orm import ChatORMHandler

log = getLogger(__name__)

router = Router()


@router.message(Command("mute"))
async def mute_user(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await MuteRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    # Получение пользователя
    user, period = await get_user_id_name_period(message, command)

    if not await RestChecker.is_mute_data_valid(user, period, message):
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
        "Попытка замутить moderator=%s user=%r chat_id=%s period=%r",
        name_in_log.user(message),
        user,
        message.chat.id,
        period,
    )

    period_time = None if period == MUTE_FOREVER else period

    async with async_session_factory() as session:
        rest = await MuteRestHandler.apply_restriction(
            session,
            moderator_id=message.from_user.id,
            chat_id=message.chat.id,
            user_id=user.id,
            period=period_time,
        )
        if rest:
            if period != MUTE_FOREVER:
                until = get_local_time() + period
                until_str = f"до {until.strftime('%Y-%m-%d %H:%M')} МСК"
            else:
                until_str = "навсегда"
            await bot.restrict_chat_member(
                message.chat.id,
                user.id,
                ChatPermissions(can_send_messages=False),
                until_date=period_time,
            )
            await session.commit()
            log.info(
                "Пользователь замучен moderator=%s user=%r chat_id=%s period=%r",
                name_in_log.user(message),
                user,
                message.chat.id,
                period,
            )

            await RestChecker.reply_n_delete(
                f"🔇 {TextMarkup.tag_user(user.name, user.id)} замучен {until_str}",
                message,
            )
        else:
            log.info(
                "Попытка замутить уже замученного moderator=%s user=%r chat_id=%s period=%r",
                name_in_log.user(message),
                user,
                message.chat.id,
                period,
            )
            await RestChecker.reply_n_delete(
                f"😆 {TextMarkup.tag_user(user.name, user.id)} уже находится в муте",
                message,
            )


@router.message(Command("unmute"))
async def unmute_user(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await MuteRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    user = await get_user_id_name(message, command)

    if not user:
        return

    # Проверка на существование пользователя
    if not await RestChecker.is_user_exists(user, message):
        return

    log.info(
        "Попытка размутить moderator=%s user=%r chat_id=%s",
        name_in_log.user(message),
        user,
        message.chat.id,
    )

    async with async_session_factory() as session:

        rest, is_unmuted = await MuteRestHandler._is_rest_exists_for_unmute(
            session, chat_id=message.chat.id, user_id=user.id
        )

        if not rest or is_unmuted:
            await session.commit()
            log.info(
                "Попытка замутить незамученного moderator=%s user=%r chat_id=%s",
                name_in_log.user(message),
                user,
                message.chat.id,
            )
            await RestChecker.reply_n_delete(
                f"😆 {TextMarkup.tag_user(user.name, user.id)} не замучен", message
            )

        else:
            user_perms = await PermRestHandler.get_by_user_chat_ids(
                session, user.id, message.chat.id
            )
            if not user_perms:
                await bot.promote_chat_member(message.chat.id, user.id)
            else:
                user_perms = permissions_to_dict(user_perms)

                await bot.restrict_chat_member(
                    message.chat.id, user.id, ChatPermissions(**user_perms)
                )
            # удаление мута из бд
            await MuteRestHandler.remove(
                session, chat_id=message.chat.id, user_id=user.id
            )
            await session.commit()
            log.info(
                "Пользователь размучен moderator=%s user=%r chat_id=%s",
                name_in_log.user(message),
                user,
                message.chat.id,
            )

            await RestChecker.reply_n_delete(
                f"✅ {TextMarkup.tag_user(user.name, user.id)} успешно размучен",
                message,
            )

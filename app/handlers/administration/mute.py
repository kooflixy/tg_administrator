from datetime import datetime
from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatPermissions, Message

from app.bot_obj import bot
from app.contrib.checkers import RestChecker
from app.contrib.for_logging import name_in_log
from app.contrib.text_markup import TextMarkup
from app.utils.contrib import (
    MUTE_FOREVER,
    get_user_id_name,
    get_user_id_name_period,
    time_text_to_seconds,
)
from app.utils.rest_handler import MuteRestHandler
from app.utils.rest_handler.ban_rest import BanRestHandler
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

    async with async_session_factory() as session:
        rest = await MuteRestHandler.apply_restriction(
            session,
            moderator_id=message.from_user.id,
            chat_id=message.chat.id,
            user_id=user.id,
            period=period,
        )
        if rest:
            if period < MUTE_FOREVER:
                until_timestamp = datetime.now().timestamp() + period
                until_date = f"до {datetime.fromtimestamp(until_timestamp).strftime('%Y-%m-%d %H:%M')}"
            else:
                until_timestamp = 0
                until_date = "навсегда"
            await bot.restrict_chat_member(
                message.chat.id,
                user.id,
                ChatPermissions(can_send_messages=False),
                until_date=until_timestamp,
            )
            await session.commit()

            await RestChecker.reply_n_delete(
                f"{TextMarkup.tag_user(user.name, user.id)} замучен {until_date}",
                message,
            )
        else:
            await RestChecker.reply_n_delete(
                f"{TextMarkup.tag_user(user.name, user.id)} уже находится в муте",
                message,
            )


@router.message(Command("unmute"))
async def unmute_user(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await MuteRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    log.debug(
        "%s решил размутить пользователя user_id=%r chat_id=%s",
        name_in_log.user(message),
        command.args,
        message.chat.id,
    )

    user = await get_user_id_name(message, command)

    # Проверка на существование пользователя
    if not await RestChecker.is_user_exists(user, message):
        return

    async with async_session_factory() as session:

        if await MuteRestHandler._is_rest_exists(
            session, chat_id=message.chat.id, user_id=user.id
        ):
            await bot.restrict_chat_member(
                message.chat.id, user.id, ChatPermissions(can_send_messages=True)
            )
            await MuteRestHandler.remove(
                session, chat_id=message.chat.id, user_id=user.id
            )
            await session.commit()

            await RestChecker.reply_n_delete(
                f"{TextMarkup.tag_user(user.name, user.id)} успешно размучен", message
            )

        else:
            await RestChecker.reply_n_delete(
                f"{TextMarkup.tag_user(user.name, user.id)} не замучен", message
            )

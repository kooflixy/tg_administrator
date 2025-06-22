from datetime import datetime, timedelta
from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatPermissions, Message

from app.bot_obj import bot
from app.contrib.checkers import RestChecker
from app.contrib.for_logging import name_in_log
from app.contrib.text_markup import TextMarkup
from app.utils.contrib import get_user_id_name_reason
from app.utils.rest_handler import MuteRestHandler, WarnRestHandler
from app.utils.rest_handler.ban_rest import BanRestHandler
from app.utils.time import get_local_time
from config import changeable_settings
from db.classes import ActionTypeEnum
from db.database import async_session_factory
from db.queries.chat_orm import ChatORMHandler

log = getLogger(__name__)

router = Router()

MUTE_TIME = timedelta(days=10)


@router.message(Command("warn"))
async def warn_user(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await WarnRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    # Получение пользователя
    user, reason = await get_user_id_name_reason(message, command)

    # Проверка на существование пользователя
    if not await RestChecker.is_user_exists(user, message):
        return

    chat_member = await bot.get_chat_member(message.chat.id, user.id)

    # Проверка, является ли пользователь участником группы
    if not await RestChecker.is_user_member(chat_member, message):
        return

    # Проверка, является ли пользователь модератором чата
    if await RestChecker.is_user_moderator(chat_member, message):
        return

    log.info(
        "Попытка дать варн moderator=%s user=%r chat_id=%s reason=%r",
        name_in_log.user(message),
        user,
        message.chat.id,
        reason,
    )

    async with async_session_factory() as session:
        # накладывание варна с добавлением его в бд
        rest = await WarnRestHandler.apply_restriction(
            session,
            moderator_id=message.from_user.id,
            chat_id=message.chat.id,
            user_id=user.id,
            reason=reason,
        )

        warn_count = await WarnRestHandler.count(
            session, chat_id=message.chat.id, user_id=user.id
        )

        is_warn_limit_exceeded = warn_count >= changeable_settings.max_warn_count

        if is_warn_limit_exceeded:
            # удаление всех варнов из бд
            await WarnRestHandler.remove(
                session, chat_id=message.chat.id, user_id=user.id
            )
            await session.commit()

            # какое наказание за превышение колва варнов
            if changeable_settings.max_warn_restriction == ActionTypeEnum.BAN:
                await bot.ban_chat_member(message.chat.id, user.id)
                await BanRestHandler.apply_restriction(
                    session,
                    moderator_id=message.from_user.id,
                    chat_id=message.chat.id,
                    user_id=user.id,
                )
                await session.commit()
                log.info(
                    "Пользователь забанен за превышение количества варнов moderator=%s user=%r chat_id=%s reason=%r",
                    name_in_log.user(message),
                    user,
                    message.chat.id,
                    reason,
                )
                await RestChecker.reply_n_delete(
                    f"🚫 {TextMarkup.tag_user(user.name, user.id)} забанен навсегда(",
                    message,
                )
            elif changeable_settings.max_warn_restriction == ActionTypeEnum.MUTE:
                rest = await MuteRestHandler.apply_restriction(
                    session,
                    moderator_id=message.from_user.id,
                    chat_id=message.chat.id,
                    user_id=user.id,
                    period=MUTE_TIME,
                )

                until = get_local_time() + MUTE_TIME
                until_str = f"до {until.strftime('%Y-%m-%d %H:%M')} МСК"
                await bot.restrict_chat_member(
                    message.chat.id,
                    user.id,
                    ChatPermissions(can_send_messages=False),
                    until_date=MUTE_TIME,
                )

                await session.commit()
                log.info(
                    "Пользователь замучен за превышение количества варнов moderator=%s user=%r chat_id=%s reason=%r",
                    name_in_log.user(message),
                    user,
                    message.chat.id,
                    reason,
                )

                await RestChecker.reply_n_delete(
                    f"🔇 {TextMarkup.tag_user(user.name, user.id)} замучен {until_str }",
                    message,
                )
        else:
            await session.commit()
            log.info(
                "Дан варн moderator=%s user=%r chat_id=%s, warn_count=%s reason=%r",
                name_in_log.user(message),
                user,
                message.chat.id,
                warn_count,
                reason,
            )
            reason_str = ""
            if reason:
                reason_str = f"\n Причина: {reason}"
            await RestChecker.reply_n_delete(
                f"😮 {TextMarkup.tag_user(user.name, user.id)} получил свой {warn_count}-й варн.{reason_str}\n До превышения осталось {changeable_settings.max_warn_count - warn_count}",
                message,
            )

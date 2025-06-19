from datetime import datetime
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
from config import changeable_settings
from db.classes import ActionTypeEnum
from db.database import async_session_factory
from db.queries.chat_orm import ChatORMHandler

log = getLogger(__name__)

router = Router()

MUTE_TIME = 60 * 60 * 24 * 10


@router.message(Command("warn"))
async def warn_user(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await WarnRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        log.debug(
            "%s попытался дать варн пользователю, но у него нет на это прав user_id=%s chat_id=%s",
            name_in_log.user(message),
            command.args,
            message.chat.id,
        )
        return

    log.debug(
        "%s решил дать варн пользователю user_id=%s chat_id=%s",
        name_in_log.user(message),
        command.args,
        message.chat.id,
    )

    # Получение пользователя
    user, reason = await get_user_id_name_reason(message, command)

    if not user:
        log.debug(
            "%s попытался дать варн пользователю, но такого пользователя не существует user_id=%s chat_id=%s",
            name_in_log.user(message),
            command.args,
            message.chat.id,
        )
        return

    # Проверка на существование пользователя
    if not await RestChecker.is_user_exists(user.id, message):
        log.debug(
            "%s попытался дать варн пользователю, но такого пользователя не существует user_id=%s chat_id=%s",
            name_in_log.user(message),
            command.args,
            message.chat.id,
        )
        return

    # Проверка, является ли пользователь участником группы
    if not await RestChecker.is_user_member(user.id, message):
        log.debug(
            "%s попытался дать варн пользователю, но он не является участником чата user_id=%s chat_id=%s",
            name_in_log.user(message),
            command.args,
            message.chat.id,
        )
        return

    # Проверка, является ли пользователь модератором чата
    if await RestChecker.is_user_moderator(user.id, message):
        log.debug(
            "%s попытался дать варн пользователю, но он является модератором user_id=%s chat_id=%s",
            name_in_log.user(message),
            command.args,
            message.chat.id,
        )
        return

    async with async_session_factory() as session:
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

        log.debug(
            "Начало проверки превышено ли количество варнов пользователя moderator=%s user_id=%s chat_id=%s warn_count=%s",
            name_in_log.user(message),
            command.args,
            message.chat.id,
            warn_count,
        )
        if is_warn_limit_exceeded:
            ban_rest = await BanRestHandler._is_rest_exists(
                session, chat_id=message.chat.id, user_id=user.id
            )
            await WarnRestHandler.remove(
                session, chat_id=message.chat.id, user_id=user.id
            )
            await session.commit()
            if ban_rest:
                await RestChecker.reply_n_delete(
                    f"{TextMarkup.tag_user(user.name, user.id)} находится в бане",
                    message,
                )
            else:
                if changeable_settings.max_warn_restriction == ActionTypeEnum.BAN:
                    await bot.ban_chat_member(message.chat.id, user.id)
                    await BanRestHandler.apply_restriction(
                        session,
                        moderator_id=message.from_user.id,
                        chat_id=message.chat.id,
                        user_id=user.id,
                    )
                    await session.commit()
                    await RestChecker.reply_n_delete(
                        f"{TextMarkup.tag_user(user.name, user.id)} забанен навсегда(",
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

                    until_timestamp = datetime.now().timestamp() + MUTE_TIME
                    until_date = f"до {datetime.fromtimestamp(until_timestamp).strftime('%Y-%m-%d %H:%M')}"
                    await bot.restrict_chat_member(
                        message.chat.id,
                        user.id,
                        ChatPermissions(can_send_messages=False),
                        until_date=until_timestamp,
                    )

                    await session.commit()

                    await RestChecker.reply_n_delete(
                        f"{TextMarkup.tag_user(user.name, user.id)} замучен {until_date }",
                        message,
                    )
        else:
            await session.commit()
            await RestChecker.reply_n_delete(
                f"{TextMarkup.tag_user(user.name, user.id)} получил свой {warn_count}-й варн.\nДо превышения осталось {changeable_settings.max_warn_count - warn_count}",
                message,
            )

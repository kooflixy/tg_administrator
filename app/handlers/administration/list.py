from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot_obj import bot
from app.utils.checkers import RestChecker
from app.utils.contrib import MUTE_FOREVER, get_user_id_name
from app.utils.rest_handler.ban_rest import BanRestHandler
from app.utils.rest_handler.mute_rest import MuteRestHandler
from app.utils.rest_handler.warn_rest import WarnRestHandler
from app.utils.telthon_manager import TelethonManager
from app.utils.text_markup import TextMarkup
from app.utils.time import utc_to_local
from db.queries.chat_orm import ChatORMHandler

log = getLogger(__name__)

router = Router()

DELETE_TIME = 60


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
                else "<b><i>Аккаунт удален<i></b>"
            )

            user_text = f"🚫 {user_str} был забанен модератором {moderator_str}\n  Дата: {utc_to_local(banned_user.created_at).strftime('%Y-%m-%d %H:%M')} МСК"
            text_list.append(user_text)

            text = "\n\n".join(text_list)
    else:
        text = "Забаненных пользователей нет:)"

    log.info("Получен список банов moderator=%s chat_id=%s", message, message.chat.id)

    await RestChecker.reply_n_delete(text, message, DELETE_TIME)


@router.message(Command("mutelist"))
async def get_mute_list(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)

    # Проверка, является ли пользователь модератором чата
    if not await RestChecker.is_user_moderator(
        chat_member, message, send_message=False
    ):
        return

    log.info(
        "Попытка получить список мутов moderator=%s chat_id=%s",
        message,
        message.chat.id,
    )

    muted_users_list = await MuteRestHandler.get_chat_all(message.chat.id)
    if muted_users_list:
        text_list = []
        for muted_user in muted_users_list:
            user = await TelethonManager.get_user(muted_user.user_id)
            if not user:
                continue
            moderator = await TelethonManager.get_user(muted_user.by_moderator_id)

            user_str = TextMarkup.tag_user(TelethonManager.get_full_name(user), user.id)
            moderator_str = (
                TextMarkup.tag_user(
                    TelethonManager.get_full_name(moderator), moderator.id
                )
                if moderator
                else "<b><i>Аккаунт удален<i></b>"
            )

            if muted_user.period >= MUTE_FOREVER:
                until_date_str = "навсегда"
            else:
                until_date_str = (
                    utc_to_local(muted_user.created_at + muted_user.period)
                    .strftime("%Y-%m-%d %H:%M")
                    .__str__()
                    + " МСК"
                )

            user_text = f"🔇 {user_str} был замучен модератором {moderator_str}\n До: {until_date_str}\n Дата: {utc_to_local(muted_user.created_at).strftime('%Y-%m-%d %H:%M')} МСК"
            text_list.append(user_text)

            text = "\n\n".join(text_list)
    else:
        text = "Замученных пользователей нет:)"

    log.info("Получен список мутов moderator=%s chat_id=%s", message, message.chat.id)

    await RestChecker.reply_n_delete(text, message, DELETE_TIME)


@router.message(Command("warnlist"))
async def get_warn_list(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)

    # Проверка, является ли пользователь модератором чата
    if not await RestChecker.is_user_moderator(
        chat_member, message, send_message=False
    ):
        return

    # Получение пользователя
    user = await get_user_id_name(message, command)

    if not user:
        return

    log.info(
        "Попытка получить список варнов пользователя moderator=%s user=%r chat_id=%s",
        message,
        user,
        message.chat.id,
    )

    warn_list = await WarnRestHandler.get_user_all(message.chat.id, user.id)

    user_str = TextMarkup.tag_user(user, user.id)

    if warn_list:
        text_list = []
        for warn in warn_list:
            moderator = await TelethonManager.get_user(warn.by_moderator_id)

            moderator_str = (
                TextMarkup.tag_user(
                    TelethonManager.get_full_name(moderator), moderator.id
                )
                if moderator
                else "<b><i>Аккаунт удален<i></b>"
            )

            reason_str = ""
            if warn.reason:
                reason_str = f"\n Причина: {warn.reason}"

            warn_text = f"⚠ Варн от модератора {moderator_str}{reason_str}\n Дата: {utc_to_local(warn.created_at).strftime('%Y-%m-%d %H:%M')} МСК"
            text_list.append(warn_text)

            text = "\n\n".join(text_list)
    else:
        text = "У пользователя нет варнов:)"

    log.info(
        "Получен список варнов пользователя moderator=%s user=%r chat_id=%s",
        message,
        user,
        message.chat.id,
    )

    await RestChecker.reply_n_delete(text, message, DELETE_TIME)

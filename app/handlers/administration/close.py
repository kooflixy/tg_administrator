from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatPermissions, Message

from app.bot_obj import bot
from app.contrib.checkers import RestChecker
from app.contrib.for_logging import name_in_log
from app.utils.contrib import current_to_new_permissions
from app.utils.rest_handler.close_rest import CloseRestHandler
from config import changeable_settings
from db.database import async_session_factory
from db.queries.chat_orm import ChatORMHandler
from db.queries.moderator_chat_orm import ModeratorChatORMHandler

log = getLogger(__name__)

router = Router()

old_permissions = dict()


@router.message(Command("close"))
async def close_chat(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await CloseRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    log.info(
        "Попытка закрыть чат moderator=%s chat_id=%s",
        name_in_log.user(message),
        message.chat.id,
    )

    chat = await bot.get_chat(message.chat.id)
    if not chat.permissions.can_send_messages:
        await RestChecker.reply_n_delete(
            changeable_settings.already_close_text, message
        )
        return

    old_permissions[str(chat.id)] = chat.permissions

    await bot.set_chat_permissions(
        message.chat.id,
        ChatPermissions(
            can_send_messages=False, can_invite_users=chat.permissions.can_invite_users
        ),
    )

    async with async_session_factory() as session:
        moderator_ids_list = (
            await ModeratorChatORMHandler.get_all_moderator_ids_in_chat(
                session, message.chat.id
            )
        )
        for moderator_id in moderator_ids_list:
            try:
                await bot.restrict_chat_member(
                    message.chat.id, moderator_id, chat.permissions
                )
            except:
                pass

    log.info(
        "Чат закрыт moderator=%s chat_id=%s", name_in_log.user(message), message.chat.id
    )

    await RestChecker.reply_n_delete(changeable_settings.close_text, message, 180)


@router.message(Command("open"))
async def close_chat(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await CloseRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    log.info(
        "Попытка открыть чат moderator=%s chat_id=%s",
        name_in_log.user(message),
        message.chat.id,
    )

    chat = await bot.get_chat(message.chat.id)
    if chat.permissions.can_send_messages:
        await RestChecker.reply_n_delete(changeable_settings.already_open_text, message)
        return

    if str(chat.id) in old_permissions:
        await bot.set_chat_permissions(message.chat.id, old_permissions[str(chat.id)])

        old_permissions.pop(str(chat.id))
    else:
        await bot.set_chat_permissions(
            message.chat.id,
            ChatPermissions(
                can_send_messages=True,
                can_invite_users=chat.permissions.can_invite_users,
            ),
        )

    log.info(
        "Чат открыт moderator=%s chat_id=%s", name_in_log.user(message), message.chat.id
    )

    await message.reply(changeable_settings.open_text)

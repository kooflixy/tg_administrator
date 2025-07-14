from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatPermissions, Message

from app.bot_obj import bot
from app.utils.checkers import RestChecker
from app.utils.for_logging import name_in_log
from app.utils.perm import permissions_to_dict
from app.utils.rest_handler.close_rest import CloseRestHandler
from app.utils.rest_handler.perm_rest import PermRestHandler
from config import changeable_settings
from db.database import async_session_factory
from db.models import ChatPermORM
from db.queries.chat_orm import ChatORMHandler
from db.queries.moderator_chat_orm import ModeratorChatORMHandler

log = getLogger(__name__)

router = Router()


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

    await bot.set_chat_permissions(
        message.chat.id,
        ChatPermissions(),
    )

    async with async_session_factory() as session:
        if not (await ChatORMHandler.get(session, message.chat.id)).perms:
            chat_perms = ChatPermORM(
                chat_id=message.chat.id,
                **permissions_to_dict((await bot.get_chat(message.chat.id)).permissions)
            )
            session.add(chat_perms)
            await session.commit()
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

        rest_users_list = await PermRestHandler.get_chat_all(message.chat.id)
        for user in rest_users_list:
            try:
                await bot.restrict_chat_member(
                    message.chat.id, user.user_id, ChatPermissions()
                )
            except:
                pass

    log.info(
        "Чат закрыт moderator=%s chat_id=%s", name_in_log.user(message), message.chat.id
    )

    await RestChecker.reply_n_delete(changeable_settings.close_text, message, 180)


@router.message(Command("open"))
async def open_chat(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await CloseRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    log.info(
        "Попытка открыть чат moderator=%s chat_id=%s",
        name_in_log.user(message),
        message.chat.id,
    )

    tchat = await bot.get_chat(message.chat.id)
    if tchat.permissions.can_send_messages:
        await RestChecker.reply_n_delete(changeable_settings.already_open_text, message)
        return
    else:
        async with async_session_factory() as session:
            chat = await ChatORMHandler.get(session, message.chat.id)
            chat_perms = permissions_to_dict(chat.perms)
            await tchat.set_permissions(ChatPermissions(**chat_perms))

            rest_users_list = await PermRestHandler.get_chat_all(message.chat.id)
            for user in rest_users_list:
                try:
                    await bot.restrict_chat_member(
                        message.chat.id,
                        user.user_id,
                        ChatPermissions(**permissions_to_dict(user)),
                    )
                except:
                    pass

    log.info(
        "Чат открыт moderator=%s chat_id=%s", name_in_log.user(message), message.chat.id
    )

    await message.reply(changeable_settings.open_text)

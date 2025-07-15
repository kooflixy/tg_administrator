from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot_obj import bot
from app.utils.checkers import RestChecker
from app.utils.contrib import get_user_id_name
from app.utils.rest_handler import BanRestHandler, BaRestHandler
from app.utils.text_markup import TextMarkup
from db.database import async_session_factory
from db.queries.chat_orm import ChatORMHandler
from db.queries.moderator_orm import ModeratorORMHandler

log = getLogger(__name__)

router = Router()


@router.message(Command("ba"))
async def ba_user(message: Message, command: CommandObject):
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

    # Проверка, является ли пользователь модератором чата
    if await RestChecker.is_user_moderator(chat_member, message):
        return

    async with async_session_factory() as session:
        # Проверка, является ли пользователь модератором чатов
        if await ModeratorORMHandler.get(session, user.id):
            return

        rest = await BaRestHandler.apply_restriction(
            session,
            moderator_id=message.from_user.id,
            user_id=user.id,
        )

        user_str = TextMarkup.tag_user(user.name, user.id)
        if rest:
            chats_list = await ChatORMHandler.get_all(session)
            for chat in chats_list:
                try:
                    await bot.ban_chat_member(chat.id, user.id)
                except:
                    log.exception(
                        "Не удалось забанить пользователя chat_id=%s user_id=%s",
                        chat.id,
                        user.id,
                    )
            await session.commit()
            await RestChecker.reply_n_delete(
                f"{user_str} успешно забанен по всей сети чатов", message
            )
        else:
            await RestChecker.reply_n_delete(
                f"{user_str} уже забанен по всей сети чатов", message
            )


@router.message(Command("unba"))
async def unba_user(message: Message, command: CommandObject):
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

    user_str = TextMarkup.tag_user(user.name, user.id)
    async with async_session_factory() as session:
        rest = await BaRestHandler._is_rest_exists(session, user.id)

        if not rest:
            await RestChecker(f"{user_str} не забанен по всей сети чатов")
            return

        await BaRestHandler.remove(session, user.id)

        bans_chat_ids_list = [
            ban.chat_id
            for ban in (await BanRestHandler.get_all_user_bans(session, user.id))
        ]
        chats_list = await ChatORMHandler.get_all(session)

        for chat in chats_list:
            if chat.id in bans_chat_ids_list:
                continue
            try:
                await bot.unban_chat_member(chat.id, user.id)
            except:
                pass

        await session.commit()

    await RestChecker.reply_n_delete(f"{user_str} успешно разбанен по сети чатов")

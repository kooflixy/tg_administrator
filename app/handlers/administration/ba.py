import asyncio
from datetime import timedelta
from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot_obj import bot
from app.utils.checkers import RestChecker
from app.utils.contrib import (
    get_user_id_name,
    get_user_id_name_reason,
    get_user_id_name_reason_url,
)
from app.utils.rest_handler import BanRestHandler, BaRestHandler
from app.utils.telthon_manager import TelethonManager
from app.utils.text_markup import TextMarkup
from config import changeable_settings
from db.database import async_session_factory
from db.queries.chat_orm import ChatORMHandler
from db.queries.moderator_orm import ModeratorORMHandler

log = getLogger(__name__)

router = Router()

TIMEOUT = timedelta(minutes=2)


@router.message(Command("ba"))
async def ba_user(message: Message, command: CommandObject):
    if message.chat.id != changeable_settings.ba_chat_id:
        return

    if not await BaRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    # Получение пользователя
    user, reason, url = await get_user_id_name_reason_url(message, command)

    if not await RestChecker.is_ba_data_valid(user, reason, url, message):
        return

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
            msgs_list = list()
            banbase_url = ''
            chats_list = await ChatORMHandler.get_all(session)
            
            # пост в канал
            if changeable_settings.ba_channel_id:
                channel = await TelethonManager.get_entity(changeable_settings.ba_channel_id)
                if channel:
                    banbase_url = f'https://t.me/{channel.username}'
                    try:
                        post_msg = await bot.send_message(
                            changeable_settings.ba_channel_id,
                            TextMarkup.get_ba_post(user.id, user.name, reason, url)
                        )
                        rest.msg_id = post_msg.message_id
                        banbase_url += f'/{post_msg.message_id}'
                    except:
                        log.exception(
                            "При попытке отправить пост о бане в канал произошла ошибка channel_id=%s user_id=%s",
                            changeable_settings.ba_channel_id,
                            user.id,
                        )
            
            for chat in chats_list:
                try:
                    await bot.ban_chat_member(chat.id, user.id)
                except:
                    log.exception(
                        "Не удалось забанить пользователя chat_id=%s user_id=%s",
                        chat.id,
                        user.id,
                    )

                # рассылка уведомлений в чаты
                msg: Message = await bot.send_message(
                    chat.id, TextMarkup.get_ba_text(user.id, user.name, banbase_url)
                )
                msgs_list.append(msg)

            await session.commit()
            await RestChecker.reply_n_delete(
                f"{user_str} успешно забанен по всей сети чатов", message
            )
            await asyncio.sleep(TIMEOUT.total_seconds())
            for msg in msgs_list:
                try:
                    await bot.delete_message(msg.chat.id, msg.message_id)
                except:
                    pass
        else:
            await RestChecker.reply_n_delete(
                f"{user_str} уже забанен по всей сети чатов", message
            )


@router.message(Command("unba"))
async def unba_user(message: Message, command: CommandObject):
    if message.chat.id != changeable_settings.ba_chat_id:
        return

    if not await BaRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
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
            await RestChecker.reply_n_delete(
                f"{user_str} не забанен по всей сети чатов", message
            )
            return

        banbase_url = ''

        # удаление поста в канале
        if changeable_settings.ba_channel_id and rest.msg_id:
            channel = await TelethonManager.get_entity(changeable_settings.ba_channel_id)
            if channel:
                banbase_url = f'https://t.me/{channel.username}'
                try:
                    await bot.delete_message(changeable_settings.ba_channel_id, rest.msg_id)
                except:
                    log.exception(
                        "При попытке удалить пост о бане в канале произошла ошибка channel_id=%s user_id=%s",
                        changeable_settings.ba_channel_id,
                        user.id,
                    )

        await BaRestHandler.remove(session, user.id)

        bans_chat_ids_list = [
            ban.chat_id
            for ban in (await BanRestHandler.get_all_user_bans(session, user.id))
        ]
        chats_list = await ChatORMHandler.get_all(session)

        msgs_list = list()
        for chat in chats_list:
            msg: Message = await bot.send_message(
                chat.id, TextMarkup.get_unba_text(user.id, user.name, banbase_url)
            )
            msgs_list.append(msg)
            if chat.id in bans_chat_ids_list:
                continue
            try:
                await bot.unban_chat_member(chat.id, user.id)
            except:
                pass

        await session.commit()

    await RestChecker.reply_n_delete(
        f"{user_str} успешно разбанен по сети чатов", message
    )

    await asyncio.sleep(TIMEOUT.total_seconds())
    for msg in msgs_list:
        try:
            await bot.delete_message(msg.chat.id, msg.message_id)
        except:
            pass

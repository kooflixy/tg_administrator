import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional

from aiogram.types import (
    ChatMemberAdministrator,
    ChatMemberBanned,
    ChatMemberLeft,
    ChatMemberOwner,
    Message,
    ResultChatMemberUnion,
)
from pydantic import validate_call

from app.bot_obj import bot
from app.utils.contrib import MUTE_FOREVER, User
from db.queries.moderator_chat_orm import ModeratorChatORMHandler


def is_page_exists(page: int, lst: list) -> bool:
    """Проверка на то что страница существует(если она не единственная)"""
    if page == 1 or lst:
        return False
    return True


class RestChecker:
    @staticmethod
    @validate_call
    async def reply_n_delete(text: str, message: Message, interval: int = 1):
        """Отвечает пользователю и через время удаляет сообщение"""
        msg = await message.reply(text)
        await asyncio.sleep(interval)
        await bot.delete_messages(message.chat.id, [msg.message_id, message.message_id])

    @classmethod
    @validate_call
    async def is_user_exists(cls, user, message: Message) -> bool:
        if user:
            return True

        await cls.reply_n_delete("Такого пользователя не существует", message)
        return False

    @classmethod
    @validate_call
    async def is_user_main_bot(cls, user_id: int, message: Message) -> bool:
        if user_id == bot.id:
            await cls.reply_n_delete("Пользователь - я", message)
            return True

        return False

    @classmethod
    @validate_call
    async def is_user_member(
        cls, chat_member: ResultChatMemberUnion, message: Message
    ) -> bool:
        if not (
            isinstance(chat_member, ChatMemberLeft)
            or isinstance(chat_member, ChatMemberBanned)
        ):
            return True

        await cls.reply_n_delete("Пользователь не состоит в группе", message)
        return False

    @classmethod
    @validate_call
    async def is_user_moderator(
        cls,
        chat_member: ResultChatMemberUnion,
        message: Message,
        send_message: bool = True,
    ) -> bool:
        if isinstance(chat_member, ChatMemberOwner) or isinstance(
            chat_member, ChatMemberAdministrator
        ):
            if send_message:
                await cls.reply_n_delete("Пользователь является модератором", message)
            return True

        if await ModeratorChatORMHandler.is_moderator(
            chat_member.user.id, message.chat.id
        ):
            if send_message:
                await cls.reply_n_delete("Пользователь является модератором", message)
            return True

        return False

    @classmethod
    @validate_call
    async def is_mute_data_valid(
        cls, user: Optional[Any], period: Optional[timedelta], message: Message
    ) -> bool:
        if message.reply_to_message:
            if not period:
                await cls.reply_n_delete("Введен неправильный формат времени", message)
                return False
        else:
            if not user and not period:
                return False
            if not user:
                await cls.reply_n_delete("Такого пользователя не существует", message)
                return False

            if not period:
                await cls.reply_n_delete("Введен неправильный формат времени", message)
                return False

        if period < timedelta(seconds=60):
            await cls.reply_n_delete("Нельзя мутить на время меньше минуты", message)
            return False

        return True

    @classmethod
    @validate_call
    async def is_linkto_data_valid(
        cls, msg_url: Optional[str], reason: Optional[str], message: Message
    ) -> bool:
        if not msg_url:
            await cls.reply_n_delete("Не введена ссылка на сообщение", message)
            return False

        if msg_url[:13] != "https://t.me/":
            await cls.reply_n_delete("Это не ссылка на сообщение", message)
            return False

        return True

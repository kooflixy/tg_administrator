from typing import overload

from aiogram.types import CallbackQuery, ChatMemberUpdated, Message


class name_in_log:
    """Класс для удобного создания имён для логов"""

    # Для пользователя
    @staticmethod
    @overload
    def user(msg: Message) -> str: ...

    @staticmethod
    @overload
    def user(callback: CallbackQuery) -> str: ...

    @staticmethod
    @overload
    def user(event: ChatMemberUpdated) -> str: ...

    @staticmethod
    def user(entity) -> str:
        if isinstance(entity, Message):
            user_id = entity.from_user.id
            user_full_name = entity.from_user.full_name
        elif isinstance(entity, CallbackQuery):
            user_id = entity.from_user.id
            user_full_name = entity.from_user.full_name
        elif isinstance(entity, ChatMemberUpdated):
            user_id = entity.new_chat_member.user.id
            user_full_name = entity.new_chat_member.user.full_name
        return f"TgUser(id={user_id}, name={user_full_name!r})"

    # Для чата
    @staticmethod
    @overload
    def chat(msg: Message) -> str: ...

    @staticmethod
    @overload
    def chat(callback: CallbackQuery) -> str: ...

    @staticmethod
    @overload
    def chat(event: ChatMemberUpdated) -> str: ...

    @staticmethod
    def chat(entity) -> str:
        if isinstance(entity, Message):
            chat_id = entity.chat.id
            chat_title = entity.chat.title
        elif isinstance(entity, CallbackQuery):
            chat_id = entity.message.chat.id
            chat_title = entity.message.chat.title
        elif isinstance(entity, ChatMemberUpdated):
            chat_id = entity.chat.id
            chat_title = entity.chat.title

        return f"Chat(id={chat_id}, title={chat_title!r})"

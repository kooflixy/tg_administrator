from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import settings
from db.queries.chat_orm import ChatORMHandler


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class IsAdminChat(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.id == settings.ADMIN_ID


class IsChatMonitored(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.type in ["group", "supergroup"]:
            if await ChatORMHandler.is_chat_monitored(message.chat.id):
                return True
        return False

from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.filters import BaseFilter
from aiogram.types import Message
from cachetools import TTLCache

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


class AntiFloodMiddleWare(BaseMiddleware):

    def __init__(self, time_limit: int = 2):
        self.limit = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ):
        if event.from_user.id == settings.ADMIN_ID:
            return await handler(event, data)

        if event.from_user.id in self.limit:
            return
        else:
            self.limit[event.from_user.id] = None
        return await handler(event, data)

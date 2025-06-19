from logging import getLogger
from typing import Optional

from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import async_session_factory
from db.models import ChatORM, ModeratorChatORM
from db.queries import BaseORMHandler

log = getLogger(__name__)


class ChatORMHandler(BaseORMHandler[ChatORM]):
    model_cls = ChatORM
    use_unique_scalars = True

    @classmethod
    async def insert(cls, session: AsyncSession, chat_id: int, chat_name: str):
        """Делает запись и возвращает записанный объект"""
        if not isinstance(chat_id, int):
            raise TypeError("chat_id должен быть int")

        if not isinstance(chat_name, str):
            raise TypeError("chat_name должен был str")

        result = await cls._insert(session, id=chat_id, name=chat_name)

        return result

    @classmethod
    async def remove(cls, session: AsyncSession, pk_value) -> None:
        """Удаляет выбранную запись"""
        query1 = delete(ModeratorChatORM).filter(ModeratorChatORM.chat_id == pk_value)
        query2 = delete(cls.model_cls).filter(cls.model_cls.id == pk_value)
        await session.execute(query1)
        await session.execute(query2)

    @classmethod
    async def get_unassigned_chat_page(
        cls, session: AsyncSession, page: int, moderator_id: int
    ) -> list[Optional[ChatORM]]:
        if not isinstance(moderator_id, int):
            raise TypeError("moderator_id должен быть int")

        subquery = select(ModeratorChatORM.chat_id).where(
            ModeratorChatORM.moderator_id == moderator_id
        )
        query = (
            select(cls.model_cls)
            .where(cls.model_cls.id.not_in(subquery))
            .order_by(desc(cls.model_cls.created_at), desc(cls.model_cls.id))
        )

        return await super()._get_page(session, page, query)

    @classmethod
    async def is_last_unassigned_chat_page(
        cls, session, page: int, moderator_id: int
    ) -> bool:
        """Получает булево значение, является ли страница последней"""
        if not isinstance(moderator_id, int):
            raise TypeError("moderator_id должен быть int")

        subquery = select(ModeratorChatORM.chat_id).where(
            ModeratorChatORM.moderator_id == moderator_id
        )
        query = select(cls.model_cls).where(cls.model_cls.id.not_in(subquery))

        return await cls._is_last_page(session=session, page=page, query=query)

    @classmethod
    async def is_chat_monitored(cls, chat_id: int) -> bool:
        async with async_session_factory() as session:
            return chat_id in await cls.get_all_id(session)

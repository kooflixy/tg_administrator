import textwrap
from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import Optional

from sqlalchemy import delete, desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import ChatORM, DistributionChatORM
from db.queries import BaseORMHandler

log = getLogger(__name__)


class DistributionChatORMHandler(BaseORMHandler[DistributionChatORM]):
    model_cls = DistributionChatORM
    use_unique_scalars = True

    @classmethod
    async def get_all_by_dist_id(
        cls, session: AsyncSession, dist_id: int
    ) -> list[DistributionChatORM]:
        query = select(DistributionChatORM).filter_by(distribution_id=dist_id)

        return await cls._get_all(session, query)

    @classmethod
    async def insert(cls, session: AsyncSession, chat_id: int, dist_id: int):
        """Делает запись и возвращает записанный объект"""
        result = await cls._insert(session, chat_id=chat_id, distribution_id=dist_id)

        return result

    @classmethod
    async def remove_by_dist_chat_ids(
        cls, session: AsyncSession, dist_id: int, chat_id: int
    ) -> None:
        """Удаляет выбранную запись"""
        query = delete(cls.model_cls).filter_by(
            distribution_id=dist_id, chat_id=chat_id
        )

        await session.execute(query)

    @classmethod
    async def get_page(
        cls, session, page: int, dist_id: int
    ) -> list[Optional[DistributionChatORM]]:
        if not isinstance(dist_id, int):
            raise TypeError("dist_id должен быть int")

        query = (
            select(cls.model_cls)
            .filter_by(distribution_id=dist_id)
            .options(selectinload(cls.model_cls.chat))
            .order_by(desc(cls.model_cls.created_at), desc(cls.model_cls.id))
        )

        return await super()._get_page(session, page, query)

    @classmethod
    async def is_last_page(cls, session: AsyncSession, page: int, dist_id: int) -> bool:
        """Получает булево значение, является ли страница последней"""
        query = text(
            f"SELECT COUNT(*) FROM {cls.model_cls.__tablename__} WHERE distribution_id={dist_id}"
        )

        return await cls._is_last_page(session=session, page=page, query=query)

    @classmethod
    async def get_unassigned_chat_page(
        cls, session: AsyncSession, page: int, dist_id: int
    ) -> list[Optional[ChatORM]]:

        subquery = select(cls.model_cls.chat_id).filter_by(distribution_id=dist_id)
        query = (
            select(ChatORM)
            .where(ChatORM.id.not_in(subquery))
            .order_by(desc(ChatORM.created_at), desc(ChatORM.id))
        )

        return await super()._get_page(session, page, query)

    @classmethod
    async def is_last_unassigned_chat_page(
        cls, session, page: int, dist_id: int
    ) -> bool:

        subquery = select(cls.model_cls.chat_id).filter_by(distribution_id=dist_id)
        query = select(func.count(ChatORM.id)).where(ChatORM.id.not_in(subquery))

        return await cls._is_last_page(session=session, page=page, query=query)

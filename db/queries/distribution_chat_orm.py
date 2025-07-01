import textwrap
from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import Optional

from sqlalchemy import desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import DistributionChatORM
from db.queries import BaseORMHandler

log = getLogger(__name__)


class DistributionChatORMHandler(BaseORMHandler[DistributionChatORM]):
    model_cls = DistributionChatORM
    use_unique_scalars = True

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

import textwrap
from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import Optional

from sqlalchemy import delete, desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import changeable_settings
from db.models import DistributionChatORM, DistributionORM
from db.queries import BaseORMHandler

log = getLogger(__name__)


class DistributionORMHandler(BaseORMHandler[DistributionORM]):
    model_cls = DistributionORM
    use_unique_scalars = True

    @classmethod
    async def insert(
        cls, session: AsyncSession, msg_id: int, interval: timedelta, text: str
    ):
        name = textwrap.shorten(text, width=25, placeholder="...")
        created_at = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        next_dist_date = created_at + interval
        return await super()._insert(
            session,
            msg_id=msg_id,
            interval=interval,
            next_dist_date=next_dist_date,
            created_at=created_at,
            name=name,
        )

    @classmethod
    async def remove(cls, session: AsyncSession, pk_value) -> None:
        """Удаляет выбранную запись"""
        query1 = delete(DistributionChatORM).filter_by(distribution_id=pk_value)
        query2 = delete(cls.model_cls).filter_by(id=pk_value)
        await session.execute(query1)
        await session.execute(query2)

    @classmethod
    async def change_activity(cls, session: AsyncSession, dist_id: int):

        query = text(
            f"""UPDATE {cls.model_cls.__tablename__}
            SET is_active = NOT is_active
            WHERE id={dist_id}"""
        )

        await session.execute(query)

    @classmethod
    async def update_dist_date(cls, session: AsyncSession):
        now = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        query = select(cls.model_cls).filter(cls.model_cls.next_dist_date <= now)
        dist_list = await cls._get_all(session, query)
        for dist in dist_list:
            dist.next_dist_date = now + dist.interval

    @classmethod
    async def get_last_distributions_list(
        cls, session: AsyncSession
    ) -> list[DistributionORM]:
        now = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        query = (
            select(cls.model_cls)
            .options(selectinload(cls.model_cls.chats))
            .filter(
                cls.model_cls.next_dist_date <= now,
                cls.model_cls.next_dist_date
                >= now
                - timedelta(seconds=changeable_settings.distribution_check_timeout),
            )
            .order_by(desc(cls.model_cls.next_dist_date))
        )

        last_dist_list = (await session.execute(query)).scalars().all()

        return last_dist_list

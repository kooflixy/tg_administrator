import textwrap
from datetime import datetime, timedelta, timezone
from logging import getLogger

from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import DistributionORM
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
    async def change_activity(cls, session: AsyncSession, dist_id: int):

        query = text(
            f"""UPDATE {cls.model_cls.__tablename__}
            SET is_active = NOT is_active
            WHERE id={dist_id}"""
        )

        await session.execute(query)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.rest_handler.base import BaseRestHandler
from db.models import BanRestORM, ModeratorChatORM


class BanRestHandler(BaseRestHandler[BanRestORM]):
    model_cls = BanRestORM

    @classmethod
    def _get_perm(cls, moderator: ModeratorChatORM) -> bool:
        return moderator.ban_perm

    @classmethod
    async def get_all_user_bans(
        cls, session: AsyncSession, user_id: int
    ) -> list[BanRestORM]:
        query = select(BanRestORM).filter_by(user_id=user_id)
        return (await session.execute(query)).scalars().all()

from typing import Union

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.rest_handler.base import BaseRestHandler
from config import changeable_settings
from db.classes import ActionTypeEnum
from db.database import async_session_factory
from db.models import BanRestORM, ModeratorChatORM, MuteRestORM, WarnRestORM


class WarnRestHandler(BaseRestHandler[WarnRestORM]):
    model_cls = WarnRestORM

    @classmethod
    async def get_user_all(cls, chat_id: int, user_id: int) -> list[WarnRestORM]:
        async with async_session_factory() as session:
            query = select(cls.model_cls).filter_by(chat_id=chat_id, user_id=user_id)

            res = (await session.execute(query)).scalars().all()
            return res

    @classmethod
    def _get_perm(cls, moderator: ModeratorChatORM) -> bool:
        return moderator.warn_perm

    @classmethod
    async def _insert_user_restriction(
        cls,
        session: AsyncSession,
        moderator_id: int,
        chat_id: int,
        user_id: int,
        reason: str,
    ):
        return await super()._insert_user_restriction(
            session, moderator_id, chat_id, user_id, reason=reason
        )

    @classmethod
    async def apply_restriction(
        cls,
        session: AsyncSession,
        moderator_id: int,
        chat_id: int,
        user_id: int,
        reason: str,
    ):
        return await cls._insert_user_restriction(
            session, moderator_id, chat_id, user_id, reason=reason
        )

    @classmethod
    async def count(cls, session: AsyncSession, chat_id: int, user_id: int) -> int:
        query = select(func.count(WarnRestORM.id)).filter_by(
            chat_id=chat_id, user_id=user_id
        )
        warn_count = (await session.execute(query)).scalar()
        return warn_count

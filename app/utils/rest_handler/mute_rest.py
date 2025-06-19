from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.contrib import MUTE_FOREVER
from app.utils.rest_handler.base import BaseRestHandler
from db.models import ModeratorChatORM, MuteRestORM


class MuteRestHandler(BaseRestHandler[MuteRestORM]):
    model_cls = MuteRestORM

    @staticmethod
    def _get_perm(moderator: ModeratorChatORM) -> bool:
        return moderator.mute_perm

    @classmethod
    async def _insert_user_restriction(
        cls,
        session: AsyncSession,
        moderator_id: int,
        chat_id: int,
        user_id: int,
        period: int,
    ):
        return await super()._insert_user_restriction(
            session, moderator_id, chat_id, user_id, period=period
        )

    @classmethod
    async def _is_rest_exists(cls, session, chat_id, user_id):
        obj = await super()._is_rest_exists(session, chat_id, user_id)
        if obj:
            if obj.period >= MUTE_FOREVER:
                return obj
            if obj.created_at.timestamp() + obj.period > datetime.now().timestamp():
                await cls.remove(session, chat_id=chat_id, user_id=user_id)
                return
        return obj

    @classmethod
    async def apply_restriction(
        cls,
        session: AsyncSession,
        moderator_id: int,
        chat_id: int,
        user_id: int,
        period: int,
    ):
        a = await super().apply_restriction(
            session, moderator_id, chat_id, user_id, period=period
        )
        return a

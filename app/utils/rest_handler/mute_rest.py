from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.contrib import MUTE_FOREVER
from app.utils.rest_handler.base import BaseRestHandler
from db.database import async_session_factory
from db.models import ModeratorChatORM, MuteRestORM


class MuteRestHandler(BaseRestHandler[MuteRestORM]):
    model_cls = MuteRestORM

    @classmethod
    async def delete_overdue(cls) -> None:
        current_time_utc = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        stmt = delete(cls.model_cls).filter(
            and_(
                cls.model_cls.period != None,
                cls.model_cls.created_at + cls.model_cls.period < current_time_utc,
            )
        )

        async with async_session_factory() as session:
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def get_chat_all(cls, chat_id: int) -> list[MuteRestORM]:
        await cls.delete_overdue()
        mutes_list = await super().get_chat_all(chat_id)
        return mutes_list

    @classmethod
    def _get_perm(cls, moderator: ModeratorChatORM) -> bool:
        return moderator.mute_perm

    @classmethod
    async def _insert_user_restriction(
        cls,
        session: AsyncSession,
        moderator_id: int,
        chat_id: int,
        user_id: int,
        period: timedelta,
    ):
        return await super()._insert_user_restriction(
            session, moderator_id, chat_id, user_id, period=period
        )

    @classmethod
    async def _is_rest_exists(cls, session, chat_id, user_id):
        await cls.delete_overdue()

        obj = await super()._is_rest_exists(session, chat_id, user_id)
        return obj

    @classmethod
    async def apply_restriction(
        cls,
        session: AsyncSession,
        moderator_id: int,
        chat_id: int,
        user_id: int,
        period: timedelta,
    ):
        await cls.delete_overdue()
        a = await super().apply_restriction(
            session, moderator_id, chat_id, user_id, period=period
        )
        return a

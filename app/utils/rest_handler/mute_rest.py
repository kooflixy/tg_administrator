from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.contrib import MUTE_FOREVER
from app.utils.rest_handler.base import BaseRestHandler
from db.database import async_session_factory
from db.models import ModeratorChatORM, MuteRestORM


class MuteRestHandler(BaseRestHandler[MuteRestORM]):
    model_cls = MuteRestORM

    @classmethod
    async def get_chat_all(cls, chat_id: int) -> list[MuteRestORM]:
        mutes_list = await super().get_chat_all(chat_id)
        not_relevance_mute_ids_list = []
        res = []
        for mute in mutes_list:
            if mute:
                if mute.period >= MUTE_FOREVER:
                    res.append(mute)
                    continue
                if mute.created_at.replace(
                    tzinfo=timezone.utc
                ) + mute.period < datetime.now(tz=timezone.utc):
                    not_relevance_mute_ids_list.append(mute.id)
                    continue
                res.append(mute)
        if not_relevance_mute_ids_list:
            async with async_session_factory() as session:
                query = delete(cls.model_cls).filter(
                    cls.model_cls.id.in_(not_relevance_mute_ids_list)
                )

                await session.execute(query)
                await session.commit()
        return res

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
        obj = await super()._is_rest_exists(session, chat_id, user_id)
        if obj:
            if obj.period >= MUTE_FOREVER:
                return obj
            is_unmuted = obj.created_at.replace(
                tzinfo=timezone.utc
            ) + obj.period < datetime.now(tz=timezone.utc)
            if is_unmuted:
                await MuteRestHandler.remove(session, chat_id, user_id)
        return obj

    @classmethod
    async def _is_rest_exists_for_unmute(cls, session, chat_id, user_id):
        obj = await super()._is_rest_exists(session, chat_id, user_id)
        is_unmuted = None
        if obj:
            if obj.period >= MUTE_FOREVER:
                return obj, False
            is_unmuted = obj.created_at.replace(
                tzinfo=timezone.utc
            ) + obj.period < datetime.now(tz=timezone.utc)
            if is_unmuted:
                await MuteRestHandler.remove(session, chat_id, user_id)
        return obj, is_unmuted

    @classmethod
    async def apply_restriction(
        cls,
        session: AsyncSession,
        moderator_id: int,
        chat_id: int,
        user_id: int,
        period: timedelta,
    ):
        a = await super().apply_restriction(
            session, moderator_id, chat_id, user_id, period=period
        )
        return a

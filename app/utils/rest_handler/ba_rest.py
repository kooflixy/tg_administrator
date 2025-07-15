from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.rest_handler.base import BaseRestHandler
from db.models import BaRestORM, ModeratorChatORM


class BaRestHandler(BaseRestHandler[BaRestORM]):
    model_cls = BaRestORM

    @classmethod
    def _get_perm(cls, moderator: ModeratorChatORM) -> bool:
        return moderator.ba_perm

    @classmethod
    async def _is_rest_exists(
        cls, session: AsyncSession, user_id: int
    ) -> Optional[BaRestORM]:
        """Проверяет, наложено ли уже ограничение(возвращает запись), может вообще не реализовываться."""
        query = select(cls.model_cls).filter_by(user_id=user_id).with_for_update()
        obj = (await session.execute(query)).scalar()
        return obj

    @classmethod
    async def _insert_user_restriction(
        cls, session: AsyncSession, moderator_id: int, user_id: int, **kwargs
    ):
        """Добавляет запись ограничения в бд"""
        rest = cls.model_cls(by_moderator_id=moderator_id, user_id=user_id, **kwargs)
        session.add(rest)
        return rest

    @classmethod
    async def apply_restriction(
        cls, session: AsyncSession, moderator_id: int, user_id: int, **kwargs
    ) -> BaRestORM:
        if not await cls._is_rest_exists(session, user_id=user_id):
            return await cls._insert_user_restriction(
                session, moderator_id=moderator_id, user_id=user_id, **kwargs
            )
        return

    @classmethod
    async def remove(cls, session: AsyncSession, user_id: int) -> None:
        query = delete(cls.model_cls).filter_by(user_id=user_id)
        await session.execute(query)

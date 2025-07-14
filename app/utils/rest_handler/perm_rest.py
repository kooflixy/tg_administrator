from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.rest_handler.base import BaseRestHandler
from db.models import ModeratorChatORM, UserPermORM


class PermRestHandler(BaseRestHandler[UserPermORM]):
    model_cls = UserPermORM

    @classmethod
    def _get_perm(moderator: ModeratorChatORM) -> bool:
        return moderator.perm_perm

    @classmethod
    async def get_by_user_chat_ids(
        cls, session: AsyncSession, user_id: int, chat_id: int
    ) -> Optional[UserPermORM]:
        query = select(cls.model_cls).filter_by(user_id=user_id, chat_id=chat_id)
        res = (await session.execute(query)).scalar()
        return res

    @classmethod
    async def change_user_perm(
        cls, session: AsyncSession, user_id: int, chat_id: int, new_perms: dict
    ):
        user_perms = await cls.get_by_user_chat_ids(session, user_id, chat_id)
        if user_perms:
            for key, value in new_perms.items():
                setattr(user_perms, key, value)
        else:
            user_perms = UserPermORM(user_id=user_id, chat_id=chat_id, **new_perms)
            session.add(user_perms)

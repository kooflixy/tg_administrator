from app.utils.rest_handler.base import BaseRestHandler
from db.models import MuteRestORM, ModeratorChatORM
from sqlalchemy.ext.asyncio import AsyncSession

class MuteRestHandler(BaseRestHandler[MuteRestORM]):
    model_cls = MuteRestORM

    @staticmethod
    def _get_perm(moderator: ModeratorChatORM) -> bool:
        return moderator.mute_perm
    
    @classmethod
    async def _insert_user_restriction(cls, session: AsyncSession, moderator_id: int, chat_id: int, user_id: int, period: int):
        return await super()._insert_user_restriction(session, moderator_id, chat_id, user_id, period=period)
    
    @classmethod
    async def apply_restriction(cls, session: AsyncSession, moderator_id: int, chat_id: int, user_id: int, period: int):
        return await super().apply_restriction(session, moderator_id, chat_id, user_id, period=period)
from sqlalchemy import select
from app.utils.rest_handler.base import BaseRestHandler
from db.models import BanRestORM, ModeratorChatORM
from sqlalchemy.ext.asyncio import AsyncSession

class BanRestHandler(BaseRestHandler[BanRestORM]):
    model_cls = BanRestORM

    @staticmethod
    def _get_perm(moderator: ModeratorChatORM) -> bool:
        return moderator.ban_perm
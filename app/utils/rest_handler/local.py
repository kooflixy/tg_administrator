from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.rest_handler.base import BaseRestHandler
from db.models import BaRestORM, ModeratorChatORM


class LocalRestHandler(BaseRestHandler[BaRestORM]):
    model_cls = BaRestORM

    @classmethod
    def _get_perm(cls, moderator: ModeratorChatORM) -> bool:
        return moderator.local_perm

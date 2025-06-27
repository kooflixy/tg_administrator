from app.utils.rest_handler.base import BaseRestHandler
from db.models import BanRestORM, ModeratorChatORM


class BanRestHandler(BaseRestHandler[BanRestORM]):
    model_cls = BanRestORM

    @classmethod
    def _get_perm(cls, moderator: ModeratorChatORM) -> bool:
        return moderator.ban_perm

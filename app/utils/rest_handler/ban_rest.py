from app.utils.rest_handler.base import BaseRestHandler
from db.models import BanRestORM, ModeratorChatORM

class BanRestHandler(BaseRestHandler[BanRestORM]):
    model_cls = BanRestORM

    @staticmethod
    def _get_perm(moderator: ModeratorChatORM) -> bool:
        return moderator.ban_perm
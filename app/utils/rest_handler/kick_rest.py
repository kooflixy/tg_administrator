from app.utils.rest_handler.base import BaseRestHandler
from db.models import ModeratorChatORM


class KickRestHandler(BaseRestHandler[None]):
    model_cls = None

    @classmethod
    def _get_perm(cls, moderator: ModeratorChatORM) -> bool:
        return moderator.kick_perm

    @classmethod
    async def _is_rest_exists(cls, *args, **kwargs):
        pass

    @classmethod
    async def _insert_user_restriction(cls, *args, **kwargs):
        pass

    @classmethod
    async def apply_restriction(cls, *args, **kwargs):
        pass

    @classmethod
    async def remove(cls, *args, **kwargs):
        pass

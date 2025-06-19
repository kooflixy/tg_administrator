from logging import getLogger

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ModeratorChatORM, ModeratorORM
from db.queries import BaseORMHandler

log = getLogger(__name__)


class ModeratorORMHandler(BaseORMHandler[ModeratorORM]):
    model_cls = ModeratorORM
    use_unique_scalars = True

    @classmethod
    async def insert(cls, session: AsyncSession, user_id: int, user_name: str):
        """Делает запись и возвращает записанный объект"""
        if not isinstance(user_id, int):
            raise TypeError("user_id должен быть int")

        if not isinstance(user_name, str):
            raise TypeError("user_name должен был str")

        result = await cls._insert(session, id=user_id, name=user_name)

        return result

    @classmethod
    async def remove(cls, session: AsyncSession, pk_value) -> None:
        """Удаляет выбранную запись"""
        query1 = delete(ModeratorChatORM).filter(
            ModeratorChatORM.moderator_id == pk_value
        )
        query2 = delete(cls.model_cls).filter(cls.model_cls.id == pk_value)

        await session.execute(query1)
        await session.execute(query2)

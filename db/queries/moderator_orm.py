from logging import getLogger

from sqlalchemy import delete
from db.models import ModeratorChatORM, ModeratorORM
from db.queries import BaseORMHandler

from sqlalchemy.ext.asyncio import AsyncSession

log = getLogger(__name__)

class ModeratorORMHandler(BaseORMHandler[ModeratorORM]):
    model_cls = ModeratorORM
    use_unique_scalars = True

    @classmethod
    async def insert(cls, session: AsyncSession, user_id: int, user_name: str):
        '''Делает запись и возвращает записанный объект'''
        if not isinstance(user_id, int):
            raise TypeError('user_id должен быть int')
        
        if not isinstance(user_name, str):
            raise TypeError('user_name должен был str')

        try:
            result = await cls._insert(session, id=user_id, name=user_name)
        except Exception as ex:
            log.error('Не удалось добавить модератора user_id=%r, user_name=%r', user_id, user_name, exc_info=True)
            raise ex

        return result
    
    @classmethod
    async def remove(cls, session: AsyncSession, pk_value) -> None:
        '''Удаляет выбранную запись'''
        query1 = (
            delete(ModeratorChatORM)
            .filter(ModeratorChatORM.moderator_id==pk_value)
        )
        query2 = (
            delete(cls.model_cls)
            .filter(cls.model_cls.id==pk_value)
        )
        try:
            await session.execute(query1)
            await session.execute(query2)
        except Exception as ex:
            log.error('При удалении %r с pk_value=%r произошла ошибка', cls.model_cls, pk_value, exc_info=True)
            raise ex
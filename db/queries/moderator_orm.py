from logging import getLogger
from db.models import ModeratorORM
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
            log.warning('Неверный тип user_id: ожидался int, но был получен %s (%r)', type(user_id), user_id)
            raise ValueError('user_id должен быть int')
        
        if not isinstance(user_name, str):
            log.warning('Неверный тип user_name: ожидался str, но был получен %r', user_name)
            raise ValueError('user_name должен был str')

        try:
            result = await cls._insert(session, id=user_id, name=user_name)
        except Exception as ex:
            log.error('Не удалось добавить модератора user_id=%r, user_name=%r', user_id, user_name, exc_info=True)
            raise ex

        return result
from logging import getLogger
from db.models import ChatORM
from db.queries import BaseORMHandler

from sqlalchemy.ext.asyncio import AsyncSession

log = getLogger(__name__)

class ModeratorORMHandler(BaseORMHandler[ChatORM]):
    model_cls = ChatORM
    use_unique_scalars = True

    @classmethod
    async def insert(cls, session: AsyncSession, chat_id: int, chat_name: str):
        '''Делает запись и возвращает записанный объект'''
        if not isinstance(chat_id, int):
            log.warning('Неверный тип chat_id: ожидался int, но был получен %s (%r)', type(chat_id), chat_id)
            raise ValueError('chat_id должен быть int')
        
        if not isinstance(chat_name, str):
            log.warning('Неверный тип chat_name: ожидался str, но был получен %r', chat_name)
            raise ValueError('chat_name должен был str')

        try:
            result = await cls._insert(session, id=chat_id, name=chat_name)
        except Exception as ex:
            log.error('Не удалось добавить модератора chat_id=%r, chat_name=%r', chat_id, chat_name, exc_info=True)
            raise ex

        return result
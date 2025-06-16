from logging import getLogger
from typing import Optional

from sqlalchemy import delete, desc, select
from db.models import ChatORM, ModeratorChatORM
from db.queries import BaseORMHandler

from sqlalchemy.ext.asyncio import AsyncSession

log = getLogger(__name__)

class ChatORMHandler(BaseORMHandler[ChatORM]):
    model_cls = ChatORM
    use_unique_scalars = True

    @classmethod
    async def insert(cls, session: AsyncSession, chat_id: int, chat_name: str):
        '''Делает запись и возвращает записанный объект'''
        if not isinstance(chat_id, int):
            raise TypeError('chat_id должен быть int')
        
        if not isinstance(chat_name, str):
            raise TypeError('chat_name должен был str')

        try:
            result = await cls._insert(session, id=chat_id, name=chat_name)
        except Exception as ex:
            log.error('Не удалось добавить модератора chat_id=%r, chat_name=%r', chat_id, chat_name, exc_info=True)
            raise ex

        return result
    
    @classmethod
    async def remove(cls, session: AsyncSession, pk_value) -> None:
        '''Удаляет выбранную запись'''
        query1 = (
            delete(ModeratorChatORM)
            .filter(ModeratorChatORM.chat_id==pk_value)
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
        
        
    @classmethod
    async def get_unassigned_chat_page(cls, session: AsyncSession, page: int, moderator_id: int) -> list[Optional[ChatORM]]:
        if not isinstance(moderator_id, int):
            raise TypeError('moderator_id должен быть int')
        
        subquery = (
            select(ModeratorChatORM.chat_id)
            .where(ModeratorChatORM.moderator_id == moderator_id)
        )
        query = (
            select(cls.model_cls)
            .where(cls.model_cls.id.not_in(subquery))
            .order_by(desc(cls.model_cls.created_at), desc(cls.model_cls.id))
        )
        
        try:
            return await super()._get_page(session, page, query)
        except Exception as ex:
            log.error('При получении страницы %s произошла ошибка, page=%r, moderator_id=%r', cls.model_cls, page, moderator_id, exc_info=ex)
            raise ex
        
    
    @classmethod
    async def is_last_unassigned_chat_page(cls, session, page: int, moderator_id: int) -> bool:
        '''Получает булево значение, является ли страница последней'''
        if not isinstance(moderator_id, int):
            raise TypeError('moderator_id должен быть int')
        
        subquery = (
            select(ModeratorChatORM.chat_id)
            .where(ModeratorChatORM.moderator_id == moderator_id)
        )
        query = (
            select(cls.model_cls)
            .where(cls.model_cls.id.not_in(subquery))
        )

        try:
            return await cls._is_last_page(session=session, page=page, query=query)
        except Exception as ex:
            log.error('При попытке узнать последняя ли страница, произошла ошибка model=%r, page=%r, moderator_id=%r', cls.model_cls, page, moderator_id, exc_info=True)
            raise ex
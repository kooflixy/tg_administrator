from logging import getLogger
from typing import Optional

from db.models import ChatORM, ModeratorChatORM
from db.queries import BaseORMHandler

from sqlalchemy import desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

log = getLogger(__name__)

class ModeratorChatORMHandler(BaseORMHandler[ModeratorChatORM]):
    model_cls = ModeratorChatORM
    use_unique_scalars = True

    @classmethod
    async def insert(cls, session: AsyncSession, moderator_id: int, chat_id: int):
        '''Делает запись и возвращает записанный объект'''
        if not isinstance(moderator_id, int):
            log.warning('Неверный тип moderator_id: ожидался int, но был получен %s (%r)', type(moderator_id), moderator_id)
            raise ValueError('moderator_id должен быть int')
        
        if not isinstance(chat_id, int):
            log.warning('Неверный тип chat_id: ожидался int, но был получен %s (%r)', type(chat_id), chat_id)
            raise ValueError('chat_id должен быть int')

        try:
            result = await cls._insert(session, moderator_id=moderator_id, chat_id=chat_id)
        except Exception as ex:
            log.error('Не удалось добавить модератора moderator_id=%r, chat_id=%r', moderator_id, chat_id, exc_info=True)
            raise ex

        return result
    
    @classmethod
    async def get_page(cls, session, page: int, moderator_id: int) -> list[Optional[ModeratorChatORM]]:
        if not isinstance(moderator_id, int):
            log.warning('Неверный тип moderator_id: ожидался int, но был получен %s (%r)', type(moderator_id), moderator_id)
            raise ValueError('moderator_id должен быть int')
        
        query = (
            select(cls.model_cls)
            .filter(cls.model_cls.moderator_id==moderator_id)
            .options(selectinload(cls.model_cls.chat))
            .order_by(desc(cls.model_cls.created_at), desc(cls.model_cls.id))
        )

        try:
            return await super()._get_page(session, page, query)
        except Exception as ex:
            log.error('При получении страницы %s произошла ошибка, page=%r, moderator_id=%r', cls.model_cls, page, moderator_id, exc_info=ex)
            raise ex
    
    
    @classmethod
    async def get_unassigned_chat_page(cls, session: AsyncSession, page: int, moderator_id: int) -> list[Optional[ModeratorChatORM]]:
        if not isinstance(moderator_id, int):
            log.warning('Неверный тип moderator_id: ожидался int, но был получен %s (%r)', type(moderator_id), moderator_id)
            raise ValueError('moderator_id должен быть int')
        
        subquery = (
            select(cls.model_cls.chat_id)
            .where(cls.model_cls.moderator_id == moderator_id)
        )
        query = (
            select(ChatORM)
            .where(ChatORM.id.not_in(subquery))
            .order_by(desc(ChatORM.created_at), desc(ChatORM.id))
        )
        
        try:
            return await super()._get_page(session, page, query)
        except Exception as ex:
            log.error('При получении страницы %s произошла ошибка, page=%r, moderator_id=%r', cls.model_cls, page, moderator_id, exc_info=ex)
            raise ex
    
    
    @classmethod
    async def is_last_page(cls, session, page: int, moderator_id: int) -> bool:
        '''Получает булево значение, является ли страница последней'''
        if not isinstance(moderator_id, int):
            log.warning('Неверный тип moderator_id: ожидался int, но был получен %s (%r)', type(moderator_id), moderator_id)
            raise ValueError('moderator_id должен быть int')
        
        query = text(f'SELECT COUNT(*) FROM {cls.model_cls.__tablename__} WHERE moderator_id={moderator_id}')
        
        try:
            return await cls._is_last_page(session=session, page=page, query=query)
        except Exception as ex:
            log.error('При попытке узнать последняя ли страница, произошла ошибка model=%r, page=%r, moderator_id=%r', cls.model_cls, page, moderator_id, exc_info=True)
            raise ex
    
    
    @classmethod
    async def is_last_unassigned_chat_page(cls, session, page: int, moderator_id: int) -> bool:
        '''Получает булево значение, является ли страница последней'''
        if not isinstance(moderator_id, int):
            log.warning('Неверный тип moderator_id: ожидался int, но был получен %s (%r)', type(moderator_id), moderator_id)
            raise ValueError('moderator_id должен быть int')
        
        subquery = (
            select(cls.model_cls.chat_id)
            .where(cls.model_cls.moderator_id == moderator_id)
        )
        query = (
            select(func.count())
            .where(ChatORM.id.not_in(subquery))
        )

        try:
            return await cls._is_last_page(session=session, page=page, query=query)
        except Exception as ex:
            log.error('При попытке узнать последняя ли страница, произошла ошибка model=%r, page=%r, moderator_id=%r', cls.model_cls, page, moderator_id, exc_info=True)
            raise ex
        
        
    @classmethod
    async def change_permission(cls, session: AsyncSession, moderator_id: int, chat_id: int, perm_name: str) -> None:
        if not isinstance(moderator_id, int):
            log.warning('Неверный тип moderator_id: ожидался int, но был получен %s (%r)', type(moderator_id), moderator_id)
            raise ValueError('moderator_id должен быть int')
        
        if not isinstance(chat_id, int):
            log.warning('Неверный тип chat_id: ожидался int, но был получен %s (%r)', type(chat_id), chat_id)
            raise ValueError('chat_id должен быть int')
        
        if not isinstance(perm_name, str):
            log.warning('Неверный тип perm_name: ожидался str, но был получен %s (%r)', type(perm_name), perm_name)
            raise ValueError('perm_name должен быть str')
        
        query = text(
            f'''UPDATE {cls.model_cls.__tablename__}
            SET {perm_name} = NOT {perm_name}
            WHERE moderator_id={moderator_id} and chat_id={chat_id}'''
        )
        try:
            await session.execute(query)
        except Exception as ex:
            log.error('При попытке изменить право %r произошла ошибка moderator_id=%r, chat_id=%r, perm_name=%r', cls.model_cls, moderator_id, chat_id, perm_name, exc_info=True)
            raise ex
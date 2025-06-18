from logging import getLogger
from typing import Optional

from db.models import ChatORM, ModeratorChatORM
from db.queries import BaseORMHandler
from db.database import async_session_factory

from sqlalchemy import delete, desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import settings

log = getLogger(__name__)

class ModeratorChatORMHandler(BaseORMHandler[ModeratorChatORM]):
    model_cls = ModeratorChatORM
    use_unique_scalars = True

    @classmethod
    async def get_all_id(cls, session):
        lst = await super().get_all_id(session)
        lst.append(settings.ADMIN_ID)
        return lst

    @classmethod
    async def get_all_moderator_ids_in_chat(cls, session: AsyncSession, chat_id: int):
        query = (
            select(ModeratorChatORM.moderator_id)
            .filter(ModeratorChatORM.chat_id==chat_id)
        )
        lst = await cls._get_all(session, query)
        lst.append(settings.ADMIN_ID)
        return lst


    @classmethod
    async def get_by_moderator_and_chat_ids(cls, session: AsyncSession, moderator_id: int, chat_id: int) -> Optional[ModeratorChatORM]:
        '''Получает одну определенную запись по pk_value'''
        query = (
            select(cls.model_cls)
            .filter(cls.model_cls.moderator_id==moderator_id, cls.model_cls.chat_id==chat_id)
            .options(selectinload(cls.model_cls.chat), selectinload(cls.model_cls.moderator))
        )

        obj = await session.execute(query)
        obj = obj.scalar()
        return obj

    @classmethod
    async def insert(cls, session: AsyncSession, moderator_id: int, chat_id: int):
        '''Делает запись и возвращает записанный объект'''
        if not isinstance(moderator_id, int):
            raise TypeError('moderator_id должен быть int')
        
        if not isinstance(chat_id, int):
            raise TypeError('chat_id должен быть int')

        result = await cls._insert(session, moderator_id=moderator_id, chat_id=chat_id)

        return result
    
    @classmethod
    async def remove_by_moderator_and_chat_ids(cls, session: AsyncSession, moderator_id: int, chat_id: int) -> None:
        '''Удаляет выбранную запись'''
        if not isinstance(moderator_id, int):
            raise TypeError('moderator_id должен быть int')
        
        if not isinstance(chat_id, int):
            raise TypeError('chat_id должен быть int')
        
        query = (
            delete(cls.model_cls)
            .filter(cls.model_cls.moderator_id==moderator_id, cls.model_cls.chat_id==chat_id)
        )

        await session.execute(query)

    @classmethod
    async def get_page(cls, session, page: int, moderator_id: int) -> list[Optional[ModeratorChatORM]]:
        if not isinstance(moderator_id, int):
            raise TypeError('moderator_id должен быть int')
        
        query = (
            select(cls.model_cls)
            .filter(cls.model_cls.moderator_id==moderator_id)
            .options(selectinload(cls.model_cls.chat))
            .order_by(desc(cls.model_cls.created_at), desc(cls.model_cls.id))
        )

        return await super()._get_page(session, page, query)
    
    
    @classmethod
    async def is_last_page(cls, session, page: int, moderator_id: int) -> bool:
        '''Получает булево значение, является ли страница последней'''
        if not isinstance(moderator_id, int):
            raise TypeError('moderator_id должен быть int')
        
        query = text(f'SELECT COUNT(*) FROM {cls.model_cls.__tablename__} WHERE moderator_id={moderator_id}')
        
        return await cls._is_last_page(session=session, page=page, query=query)
        
        
    @classmethod
    async def change_permission(cls, session: AsyncSession, moderator_id: int, chat_id: int, perm_name: str) -> None:
        if not isinstance(moderator_id, int):
            raise TypeError('moderator_id должен быть int')
        
        if not isinstance(chat_id, int):
            raise TypeError('chat_id должен быть int')
        
        if not isinstance(perm_name, str):
            raise TypeError('perm_name должен быть str')
        
        query = text(
            f'''UPDATE {cls.model_cls.__tablename__}
            SET {perm_name} = NOT {perm_name}
            WHERE moderator_id={moderator_id} and chat_id={chat_id}'''
        )

        await session.execute(query)

    @classmethod
    async def is_moderator(cls, user_id: int, chat_id: int) -> bool:
        async with async_session_factory() as session:
            return user_id in await cls.get_all_moderator_ids_in_chat(session, chat_id)
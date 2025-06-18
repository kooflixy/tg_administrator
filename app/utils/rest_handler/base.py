from abc import ABC, abstractmethod
from typing import Generic, Optional, Type, TypeVar
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import ModeratorChatORM
from db.queries import ModeratorChatORMHandler
from db.database import async_session_factory, Base

ModelType = TypeVar('ModelType', bound=Base)

class BaseRestHandler(Generic[ModelType], ABC):
    model_cls: Optional[Type[ModelType]]

    @classmethod
    @abstractmethod
    def _get_perm(cls, moderator: ModeratorChatORM) -> bool:
        '''В каждом классе своя реализация. Ожидается что-то вроде "return moderator.ba_perm" с указанием нужного права'''

    @classmethod
    async def is_perm_exists(cls, moderator_id: int, chat_id: int) -> bool:
        if moderator_id == settings.ADMIN_ID: return True

        async with async_session_factory() as session:
            moderator = await ModeratorChatORMHandler.get_by_moderator_and_chat_ids(session, moderator_id=moderator_id, chat_id=chat_id)
            if not moderator:
                return False
            return cls._get_perm(moderator)

    @classmethod
    async def _is_rest_exists(cls, session: AsyncSession, chat_id: int, user_id: int) -> Optional[ModelType]:
        '''Проверяет, наложено ли уже ограничение(возвращает запись), может вообще не реализовываться.'''
        query = (
            select(cls.model_cls)
            .filter(cls.model_cls.chat_id==chat_id, cls.model_cls.user_id==user_id)
            .with_for_update()
        )
        obj = (await session.execute(query)).scalar()
        return obj

    @classmethod
    async def _insert_user_restriction(cls, session: AsyncSession, moderator_id: int, chat_id: int, user_id: int, **kwargs):
        '''Добавляет запись ограничения в бд'''
        rest = cls.model_cls(by_moderator_id=moderator_id, chat_id=chat_id, user_id=user_id, **kwargs)
        session.add(rest)
        return rest

    @classmethod
    async def apply_restriction(cls, session: AsyncSession, moderator_id: int, chat_id: int, user_id: int, **kwargs) -> ModelType:
        if not await cls._is_rest_exists(session, chat_id=chat_id, user_id=user_id):
            return await cls._insert_user_restriction(session, moderator_id=moderator_id, chat_id=chat_id, user_id=user_id, **kwargs)
        return
    
    @classmethod
    async def remove(cls, session: AsyncSession, chat_id: int, user_id: int) -> None:
        query = (
            delete(cls.model_cls)
            .filter(cls.model_cls.chat_id==chat_id, cls.model_cls.user_id==user_id)
        )
        await session.execute(query)
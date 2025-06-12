from typing import Optional
from sqlalchemy import delete, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatORM, ModeratorORM
from config import changeable_settings

class AsyncORM:
    @staticmethod
    async def get_chat_list(session: AsyncSession) -> list[ChatORM]:
        '''Получение всех записей чатов из бд в формате ChatORM'''
        query = select(ChatORM)
        chat_list = (await session.execute(query)).scalars().all()
        return chat_list

    @staticmethod
    async def get_chat_list_page(session: AsyncSession, page: int) -> list[Optional[ChatORM]]:
        '''Получение определенного количества чатов для страницы, отсортированных по времени создания в обратном порядке'''
        query = (
            select(ChatORM)
            .order_by(desc(ChatORM.created_at), desc(ChatORM.id))
            .offset(changeable_settings.max_count_in_page * (page-1))
            .limit(changeable_settings.max_count_in_page)
        )
        chat_list = (await session.execute(query)).scalars().all()
        return chat_list

    @staticmethod
    async def get_chat_id_list(session: AsyncSession) -> list[Optional[int]]:
        '''Получение списка '''
        query = (
            select(ChatORM.id)
        )
        chat_list = (await session.execute(query)).scalars().all()
        return chat_list

    @staticmethod
    async def get_chat(session: AsyncSession, chat_id: int) -> Optional[ChatORM]:
        chat = await session.get(ChatORM, chat_id)
        return chat

    @staticmethod
    async def insert_chat(session: AsyncSession, chat_id: int, chat_name: str) -> None:
        chat = ChatORM(id=chat_id, name=chat_name)
        session.add(chat)
    
    @staticmethod
    async def remove_chat(session: AsyncSession, chat_id: int) -> None:
        query = (
            delete(ChatORM)
            .filter(ChatORM.id == chat_id)
        )
        await session.execute(query)


    @staticmethod
    async def get_moderator_list_page(session: AsyncSession, page: int) -> list[Optional[ModeratorORM]]:
        '''Получение определенного количества модераторов для страницы, отсортированных по времени создания в обратном порядке'''
        query = (
            select(ModeratorORM)
            .order_by(desc(ModeratorORM.created_at), desc(ModeratorORM.id))
            .offset(changeable_settings.max_count_in_page * (page-1))
            .limit(changeable_settings.max_count_in_page)
        )
        moderator_list = (await session.execute(query)).scalars().unique().all()
        return moderator_list

    @staticmethod
    async def get_moderator_id_list(session: AsyncSession) -> list[Optional[int]]:
        query = (
            select(ModeratorORM.id)
        )
        moderator_list = (await session.execute(query)).scalars().all()
        return moderator_list
    
    @staticmethod
    async def insert_moderator(session: AsyncSession, user_id: int, user_full_name: str) -> None:
        new_moderator = ModeratorORM(id=user_id, name=user_full_name)
        session.add(new_moderator)

        await session.commit()
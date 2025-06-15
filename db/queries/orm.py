'''Не используется'''



from typing import Optional
from sqlalchemy import and_, delete, func, select, desc, text, union
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatORM, ModeratorORM, LnkChatModeratorORM
from db.database import Base
from config import changeable_settings

class AsyncORM:
    @staticmethod
    async def get_chat_list(session: AsyncSession) -> list[ChatORM]:
        '''Получение всех записей чатов из бд в формате ChatORM'''
        query = select(ChatORM)
        chat_list = (await session.execute(query)).scalars().unique().all()
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
        chat_list = (await session.execute(query)).scalars().unique().all()
        return chat_list

    @staticmethod
    async def get_chat_id_list(session: AsyncSession) -> list[Optional[int]]:
        '''Получение списка айди чатов'''
        query = (
            select(ChatORM.id)
        )
        chat_list = (await session.execute(query)).scalars().unique().all()
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
        query1 = (
            delete(ChatORM)
            .filter(ChatORM.id==chat_id)
        )
        query2 = (
            delete(LnkChatModeratorORM)
            .filter(LnkChatModeratorORM.chat_id==chat_id)
        )

        query = union(query1, query2)
        await session.execute(query)
        await session.commit()


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
    async def get_moderator(session: AsyncSession, user_id: int) -> Optional[ModeratorORM]:
        moderator = await session.get(ModeratorORM, user_id)
        return moderator

    @staticmethod
    async def insert_moderator(session: AsyncSession, user_id: int, user_full_name: str) -> None:
        new_moderator = ModeratorORM(id=user_id, name=user_full_name)
        session.add(new_moderator)

    @staticmethod
    async def remove_moderator(session: AsyncSession, user_id: int) -> None:
        await session.execute(delete(ModeratorORM).filter(ModeratorORM.id==user_id))
    
    @staticmethod
    async def get_moderator_chat_list_page(session: AsyncSession, page: int, moderator_id: int) -> list[Optional[LnkChatModeratorORM]]:
        '''Получение определенного количества модерируемых чатов для страницы, отсортированных по времени создания в обратном порядке'''
        query = (
            select(LnkChatModeratorORM)
            .filter(LnkChatModeratorORM.moderator_id==moderator_id)
            .options(selectinload(LnkChatModeratorORM.chat))
            .order_by(desc(LnkChatModeratorORM.created_at), desc(LnkChatModeratorORM.id))
            .offset(changeable_settings.max_count_in_page * (page-1))
            .limit(changeable_settings.max_count_in_page)
        )
        moderator_list = (await session.execute(query)).scalars().all()
        return moderator_list
        
    @staticmethod
    async def get_add_moderator_chat_list_page(session: AsyncSession, page: int, moderator_id: int) -> list[Optional[ChatORM]]:
        '''Получение определенного количества чатов, возможных для добавления в модерируемые, для страницы, отсортированных по времени создания в обратном порядке'''
        subquery = (
            select(LnkChatModeratorORM.chat_id)
            .where(LnkChatModeratorORM.moderator_id == moderator_id)
        )
        query = (
            select(ChatORM)
            .where(ChatORM.id.not_in(subquery))
            .order_by(desc(ChatORM.created_at), desc(ChatORM.id))
            .offset(changeable_settings.max_count_in_page * (page-1))
            .limit(changeable_settings.max_count_in_page)
        )
        chat_list = (await session.execute(query)).scalars().unique().all()
        return chat_list
    
    @staticmethod
    async def get_moderator_chat(session: AsyncSession, moderator_id: int, chat_id: int) -> Optional[LnkChatModeratorORM]:
        query = (
            select(LnkChatModeratorORM)
            .options(selectinload(LnkChatModeratorORM.chat), selectinload(LnkChatModeratorORM.moderator))
            .filter(LnkChatModeratorORM.moderator_id==moderator_id, LnkChatModeratorORM.chat_id==chat_id)
        )
        moderator_chat = (await session.execute(query)).scalar_one_or_none()
        return moderator_chat
    
    @staticmethod
    async def insert_moderator_chat(session: AsyncSession, moderator_id: int, chat_id: int) -> None:
        moderator_chat = LnkChatModeratorORM(moderator_id=moderator_id, chat_id=chat_id)
        session.add(moderator_chat)
    
    @staticmethod
    async def remove_moderator_chat(session: AsyncSession, moderator_id: int, chat_id: int) -> None:
        await session.execute(delete(LnkChatModeratorORM).filter(LnkChatModeratorORM.moderator_id==moderator_id, LnkChatModeratorORM.chat_id==chat_id))

    @staticmethod
    async def change_moderator_chat_permission(session: AsyncSession, moderator_id: int, chat_id: int, perm_name: str) -> None:
        query = text(
            f'''UPDATE {LnkChatModeratorORM.__tablename__}
            SET {perm_name} = NOT {perm_name}
            WHERE moderator_id={moderator_id} and chat_id={chat_id}'''
        )

        await session.execute(query)

    @staticmethod
    async def is_last_page_orm(session: AsyncSession, model: Base, page: int) -> bool:
        '''Проверка, является ли страница последней'''
        query = text(f'SELECT COUNT(*) FROM {model.__tablename__}')
        records_num = (await session.execute(query)).scalar()
        if records_num-changeable_settings.max_count_in_page*page<=0:
            return True
        return False
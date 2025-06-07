from typing import Optional
from sqlalchemy import delete, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatORM
from config import changeable_settings

class AsyncORM:
    @staticmethod
    async def get_chat_list(session: AsyncSession) -> list[ChatORM]:
        query = select(ChatORM)
        chat_list = (await session.execute(query)).scalars().all()
        return chat_list

    @staticmethod
    async def get_chat_list_page(session: AsyncSession, page: int) -> Optional[list[ChatORM]]:
        query = (
            select(ChatORM)
            .order_by(desc(ChatORM.created_at), desc(ChatORM.id))
            .offset(changeable_settings.max_chat_count_in_page * (page-1))
            .limit(changeable_settings.max_chat_count_in_page)
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
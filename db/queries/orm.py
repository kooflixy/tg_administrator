from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatORM

class AsyncORM:
    
    @staticmethod
    async def insert_chat(session: AsyncSession, chat_id: int) -> None:
        chat = ChatORM(chat_id=chat_id)
        session.add(chat)
    
    @staticmethod
    async def remove_chat(session: AsyncSession, chat_id: int) -> None:
        query = (
            delete(ChatORM)
            .filter(ChatORM.chat_id == chat_id)
        )
        await session.execute(query)
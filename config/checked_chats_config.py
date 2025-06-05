from sqlalchemy import delete
from db.database import session_factory, async_session_factory
from db.models import ChatORM
from db.queries.orm import AsyncORM

class CheckedChats:
    def __init__(self):
        with session_factory() as session:
            chat_list = session.query(ChatORM.chat_id).all()
            self.chat_list: list[int] = [chat[0] for chat in chat_list]
    

    async def add_chat(self, chat_id: int) -> None:
        if chat_id in self.chat_list: return # нужно сделать исключение
        async with async_session_factory() as session:
            await AsyncORM.insert_chat(session, chat_id)
            await session.commit()
        
        self.chat_list.append(chat_id)
    
    
    async def remove_chat(self, chat_id: int) -> None:
        if chat_id not in self.chat_list: return # нужно сделать исключение
        async with async_session_factory() as session:
            await AsyncORM.remove_chat(session, chat_id)
            await session.commit()

        self.chat_list.remove(chat_id)


checked_chats = CheckedChats()
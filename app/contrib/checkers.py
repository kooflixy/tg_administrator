import asyncio
from typing import Optional
from aiogram.types import Message
from pydantic import validate_call

from app.bot_obj import bot
from db.queries.moderator_chat_orm import ModeratorChatORMHandler

def is_page_exists(page: int, lst: list) -> bool:
    '''Проверка на то что страница существует(если она не единственная)'''
    if page == 1 or lst:
        return False
    return True



class RestChecker:
    @staticmethod
    @validate_call
    async def reply_n_delete(text: str, message: Message):
        '''Отвечает пользователю и через время удаляет сообщение'''
        msg = await message.reply(text)
        await asyncio.sleep(10)
        await bot.delete_messages(message.chat.id, [msg.message_id, message.message_id])
    
    @classmethod
    @validate_call
    async def is_user_exists(cls, user_id: Optional[int], message: Message) -> bool:
        if user_id: return True

        await cls.reply_n_delete('Такого пользователя не существует', message)
        return False
    
    @classmethod
    @validate_call
    async def is_user_main_bot(cls, user_id: int, message: Message) -> bool:
        if user_id == bot.id: 
            await cls.reply_n_delete('Вы не можете удалить меня', message)
            return True

        return False
    
    @classmethod
    @validate_call
    async def is_user_member(cls, user_id: int, message: Message) -> bool:
        if await bot.get_chat_member(message.chat.id, user_id): True

        await cls.reply_n_delete('Пользователь не состоит в группе', message)
        return False

    @classmethod
    @validate_call
    async def is_user_moderator(cls, user_id: int, message: Message) -> bool:
        if await ModeratorChatORMHandler.is_moderator(user_id, message.chat.id):
            await cls.reply_n_delete('Пользователь является модератором', message)
            return True

        return False
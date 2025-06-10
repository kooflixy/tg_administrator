from logging import getLogger
from aiogram import Router
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from app.contrib.for_logging import name_in_log
from app.handlers.captcha import captcha_check
from config import changeable_settings
from db.queries.orm import AsyncORM
from db.database import async_session_factory

log = getLogger(__name__)

router = Router()

@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def react_new_member(event: ChatMemberUpdated):
    # Проверка группы на отслеживаемость
    async with async_session_factory() as session:
        chat_id_list = await AsyncORM.get_chat_id_list(session)
        chat_id = int(str(event.chat.id)[4:])
        if chat_id not in chat_id_list: return

    log.info('%s вошел в чат %s',
                name_in_log.user(event), name_in_log.chat(event))
    
    if changeable_settings.captcha_status: 
        await captcha_check(event)
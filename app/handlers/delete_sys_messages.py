from logging import getLogger
from aiogram import Router
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from app.contrib.for_logging import name_in_log
from app.handlers.captcha import captcha_check

log = getLogger(__name__)

router = Router()

@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def react_new_member(event: ChatMemberUpdated):
    log.info('%s вошел в чат %s',
                name_in_log.user(event), name_in_log.chat(event))
    
    await captcha_check(event)
from logging import getLogger

from aiogram import Router
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from app.contrib.for_logging import name_in_log
from app.handlers.captcha import captcha_check
from config import changeable_settings
from db.queries import ChatORMHandler

log = getLogger(__name__)

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def react_new_member(event: ChatMemberUpdated):
    if not await ChatORMHandler.is_chat_monitored(event.chat.id):
        return

    log.info("%s вошел в чат %s", name_in_log.user(event), name_in_log.chat(event))

    if changeable_settings.captcha_status:
        await captcha_check(event)

from logging import getLogger

from aiogram import F, Router
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated, ChatPermissions, Message

from app.bot_obj import bot
from app.handlers.captcha import captcha_check
from app.utils.for_logging import name_in_log
from app.utils.perm import permissions_to_dict
from app.utils.rest_handler.mute_rest import MuteRestHandler
from app.utils.rest_handler.perm_rest import PermRestHandler
from config import changeable_settings
from db.database import async_session_factory
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

    # применение мута или других ограничений пользователя, если они были до бана/кика
    async with async_session_factory() as session:
        mute_rest = await MuteRestHandler._is_rest_exists(
            session, event.chat.id, event.new_chat_member.user.id
        )
        if mute_rest:
            await bot.restrict_chat_member(
                event.chat.id,
                event.new_chat_member.user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=(
                    mute_rest.created_at + mute_rest.period
                    if mute_rest.period
                    else None
                ),
            )
        else:
            user_perms = await PermRestHandler.get_by_user_chat_ids(
                session,
                event.new_chat_member.user.id,
                event.chat.id,
            )
            if user_perms:
                user_perms = permissions_to_dict(user_perms)
                await bot.restrict_chat_member(
                    event.chat.id,
                    event.new_chat_member.user.id,
                    permissions=ChatPermissions(**user_perms),
                )


@router.message(
    F.new_chat_title
    | F.new_chat_photo
    | F.delete_chat_photo
    | F.pinned_message
    | F.group_chat_created
    | F.supergroup_chat_created
    | F.new_chat_members
    | F.left_chat_member
    | F.chat_invite_link
    | F.new_chat_description
)
async def handle_system_messages(message: Message):
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        log.exception(
            f"Ошибка при удалении системного сообщения chat_id=%s message_id=%s",
            message.chat.id,
            message.message_id,
        )

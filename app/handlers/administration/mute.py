from datetime import datetime
from logging import getLogger

from aiogram import Router
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject

from app.contrib.checkers import RestChecker
from app.contrib.for_logging import name_in_log
from app.contrib.text_markup import TextMarkup
from app.utils.contrib import get_user_id_name, get_user_id_name_period, time_text_to_seconds
from app.utils.rest_handler import MuteRestHandler
from app.utils.rest_handler.ban_rest import BanRestHandler
from db.queries.chat_orm import ChatORMHandler
from db.database import async_session_factory
from app.bot_obj import bot


log = getLogger(__name__)

router = Router()

@router.message(Command('mute'))
async def mute_user(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id): return

    if not await MuteRestHandler.is_perm_exists(message.from_user.id, message.chat.id): return

    log.debug('%s решил замутить пользователя user_id=%r chat_id=%s', name_in_log.user(message), command.args, message.chat.id)

    # Получение пользователя
    print(command.args, message.entities)
    user, period = await get_user_id_name_period(message, command)

    if not await RestChecker.is_mute_data_valid(user, period, message): return

    await message.answer(f'{user.name} {str(period)}')

    if not user: return

    # Проверка, является ли пользователь текущим ботом
    if await RestChecker.is_user_main_bot(user.id, message): return

    # Проверка, является ли пользователь участником группы
    if not await RestChecker.is_user_member(user.id, message): return

    # Проверка, является ли пользователь модератором чата
    if await RestChecker.is_user_moderator(user.id, message): return
    
    async with async_session_factory() as session:
        ban_rest = await BanRestHandler._is_rest_exists(session, chat_id=message.chat.id, user_id=user.id)
        if ban_rest:
            await RestChecker.reply_n_delete(f'{TextMarkup.tag_user(user.name, user.id)} находится в бане', message)
            return

        rest = await MuteRestHandler.apply_restriction(session, moderator_id=message.from_user.id, chat_id=message.chat.id, user_id=user.id, period=period)
        until_timestamp = datetime.timestamp()+period
        if rest:
            await bot.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=False, can_send_audios=False, can_send_documents=False, can_send_photos=False, can_send_videos=False, can_send_video_notes=False, can_send_voice_notes=False, can_send_polls=False, can_send_other_messages=False), until_date=until_timestamp)
            await session.commit()

            await RestChecker.reply_n_delete(f'{TextMarkup.tag_user(user.name, user.id)} замучен до {datetime.fromtimestamp(until_timestamp)}', message)
        else:
            await RestChecker.reply_n_delete(f'{TextMarkup.tag_user(user.name, user.id)} уже находится в муте', message)
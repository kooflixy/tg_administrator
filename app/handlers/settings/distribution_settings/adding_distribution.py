from datetime import timedelta
from logging import getLogger

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot_obj import bot
from app.handlers.user_commands import settings_cmd
from app.keyboards.settings.captcha import *
from app.keyboards.settings.distribution import (
    AddDistributionChatCD,
    AddDistributionChatListCD,
    ChangeDistributionActivityCD,
    DistributionChatListCD,
    DistributionDetailsCD,
    RemoveDistributionCD,
    RemoveDistributionChatCD,
    ShowDistributionCD,
    add_distribution_chat_list_ikb,
    distribution_chat_list_ikb,
    distribution_details_ikb,
    distribution_list_ikb,
)
from app.keyboards.settings_menu import DistributionListCD
from app.utils.answer_templates import error_cb_ans
from app.utils.contrib import time_text_to_seconds
from app.utils.for_logging import name_in_log
from config import settings
from db.database import async_session_factory
from db.models import DistributionORM
from db.queries.distribution_chat_orm import DistributionChatORMHandler
from db.queries.distribution_orm import DistributionORMHandler

log = getLogger(__name__)

router = Router()


@router.message(Command("add_dist"))
async def add_dist(message: Message, command: CommandObject):

    if not message.reply_to_message:
        return

    # Проверка, является ли пользователь главным админом
    if message.chat.id != settings.ADMIN_ID:
        return

    interval = time_text_to_seconds(command.args)

    if not interval:
        return

    interval = timedelta(seconds=interval)

    async with async_session_factory() as session:
        await DistributionORMHandler.insert(
            session,
            msg_id=message.reply_to_message.message_id,
            interval=interval,
            text=message.reply_to_message.text,
        )
        await session.commit()

    await message.answer("Рассылка успешно добавлена!")

from datetime import timedelta
from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.utils.contrib import time_text_to_seconds
from config import settings
from db.database import async_session_factory
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

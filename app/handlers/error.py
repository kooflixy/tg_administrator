import asyncio
from datetime import datetime
from logging import getLogger
from typing import Union

from aiogram import Router
from aiogram.types import CallbackQuery, ErrorEvent, Message

from app.bot_obj import bot
from config import settings

log = getLogger(__name__)

router = Router()

ERR_MESSAGE = "⚠Произошла ошибка"


@router.error()
async def global_error_handler(event: ErrorEvent):

    log.exception(
        "При обработке произошла непредвиденная ошибка", exc_info=event.exception
    )

    await bot.send_message(
        settings.ADMIN_ID,
        f"""Произошла непредвиденная ошибка, обратитесь разработчику
Ошибка: <b>{event.exception.__class__.__name__}</b>
Описание: <b>{event.exception}</b>
Время логирования: <b>{datetime.now()}</b>""",
    )

    try:
        if event.update.callback_query:
            await event.update.callback_query.answer(ERR_MESSAGE)
            log.info(
                "Пользователю было отправлено сообщение о произошедшей ошибке type=%r exception=%r",
                "callback_query",
                event.exception.__class__.__name__,
            )
        if event.update.message:
            msg = await event.update.message.answer(ERR_MESSAGE)
            await asyncio.sleep(10)
            await bot.delete_message(event.update.message.chat.id, msg.message_id)
            log.info(
                "Пользователю было отправлено сообщение о произошедшей ошибке type=%r exception=%r",
                "message",
                event.exception.__class__.__name__,
            )
        # В будущем возможно добавление типов
    except Exception as ex:
        log.exception(
            "При попытке отправить сообщение об ошибке пользователю произошла ошибка",
            exc_info=ex,
        )

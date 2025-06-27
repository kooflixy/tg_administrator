import asyncio
from datetime import datetime
from logging import getLogger
from typing import Union

from aiogram import Router
from aiogram.exceptions import TelegramNetworkError
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

    if isinstance(event.exception, TelegramNetworkError):
        pass
    else:
        for adm_id in list(set([settings.ADMIN_ID, settings.DEVELOPER_ID])):
            await bot.send_message(
                adm_id,
                f"""Произошла непредвиденная ошибка, обратитесь разработчику
Ошибка: <b>{event.exception.__class__.__name__}</b>
Описание: <b>{event.exception}</b>
Время логирования: <b>{datetime.now()}</b>""",
            )

    try:
        if event.update.callback_query:
            if isinstance(event.exception, TelegramNetworkError):
                await event.update.callback_query.answer(
                    f"{ERR_MESSAGE} соединения: попробуйте еще раз"
                )
            else:
                await event.update.callback_query.answer(ERR_MESSAGE)
            log.info(
                "Пользователю было отправлено сообщение о произошедшей ошибке type=%r exception=%r",
                "callback_query",
                event.exception.__class__.__name__,
            )
        if event.update.message:
            if isinstance(event.exception, TelegramNetworkError):
                msg = await event.update.message.answer(
                    f"{ERR_MESSAGE} соединения: попробуйте еще раз"
                )
            else:
                msg = await event.update.message.answer(ERR_MESSAGE)
            await asyncio.sleep(1)
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

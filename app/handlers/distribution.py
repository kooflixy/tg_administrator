import asyncio
from logging import getLogger

from aiogram.exceptions import TelegramBadRequest

from app.bot_obj import bot
from config import changeable_settings, settings
from db.database import async_session_factory
from db.queries.distribution_orm import DistributionORMHandler

log = getLogger(__name__)


async def distribution():
    async with async_session_factory() as session:
        await DistributionORMHandler.update_dist_date(session)
        await session.commit()
    while True:
        try:
            log.debug("Начало нового цикла проверки рассылки")
            await asyncio.sleep(changeable_settings.distribution_check_timeout)

            async with async_session_factory() as session:
                dist_list = await DistributionORMHandler.get_last_distributions_list(
                    session
                )
                await DistributionORMHandler.update_dist_date(session)
                await session.commit()
                if not dist_list:
                    continue
                for dist in dist_list:
                    await session.refresh(dist)
                    if not dist.is_active:
                        continue
                    for chat in dist.chats:
                        try:
                            msg_id = (
                                await bot.copy_message(
                                    chat.chat_id, settings.ADMIN_ID, dist.msg_id
                                )
                            ).message_id
                            if chat.last_msg_id:
                                await bot.delete_message(chat.chat_id, chat.last_msg_id)
                            chat.last_msg_id = msg_id
                        except:
                            log.exception(
                                "При попытке разослать сообщение из рассылки произошла ошибка: dist_id=%s",
                                dist.id,
                            )
                    log.info(
                        "Рассылка была успешно разослана в чаты dist_id=%s dist_name=%r",
                        dist.id,
                        dist.name,
                    )
                    await session.commit()
        except:
            log.exception(
                "При попытке обработать новый цикл проверки рассылки произошла ошибка"
            )

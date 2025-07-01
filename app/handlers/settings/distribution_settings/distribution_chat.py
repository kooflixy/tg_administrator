from logging import getLogger

from aiogram import Router
from aiogram.types import CallbackQuery

from app.keyboards.settings.distribution import (
    DistributionChatListCD,
    RemoveDistributionChatCD,
    distribution_chat_list_ikb,
)
from app.utils.for_logging import name_in_log
from db.database import async_session_factory
from db.queries.distribution_chat_orm import DistributionChatORMHandler

log = getLogger(__name__)

router = Router()


@router.callback_query(DistributionChatListCD.filter())
async def get_distribution_chat_list(
    callback: CallbackQuery, callback_data: DistributionChatListCD
):
    log.debug(
        "%s пытается получить %s страницу чатов рассылки dist_id=%s",
        name_in_log.user(callback),
        callback_data.cur_page,
        callback_data.dist_id,
    )

    # Получение списка чатов для страницы
    async with async_session_factory() as session:
        chat_list = await DistributionChatORMHandler.get_page(
            session, callback_data.cur_page, callback_data.dist_id
        )
        is_last_page = await DistributionChatORMHandler.is_last_page(
            session, callback_data.cur_page, callback_data.dist_id
        )

    await callback.message.edit_text(
        "📋Список чатов рассылки:",
        reply_markup=distribution_chat_list_ikb(
            chat_list, callback_data.cur_page, callback_data.dist_id, is_last_page
        ),
    )
    log.info(
        "%s получил %s страницу чатов рассылки dist_id=%s",
        name_in_log.user(callback),
        callback_data.cur_page,
        callback_data.dist_id,
    )


@router.callback_query(RemoveDistributionChatCD.filter())
async def remove_distribution_chat(
    callback: CallbackQuery, callback_data: RemoveDistributionChatCD
):
    log.debug(
        "%s пытается удалить чат рассылки dist_id=%s chat_id=%s",
        name_in_log.user(callback),
        callback_data.dist_id,
        callback_data.chat_id,
    )

    async with async_session_factory() as session:
        await DistributionChatORMHandler.remove_by_dist_chat_ids(
            session,
            dist_id=callback_data.dist_id,
            chat_id=callback_data.chat_id,
        )
        await session.commit()

    await callback.answer("Чат удален из рассылки")

    await get_distribution_chat_list(
        callback,
        DistributionChatListCD(
            cur_page=callback_data.back_page, dist_id=callback_data.dist_id
        ),
    )

    log.info(
        "%s удалил чат рассылки dist_id=%s chat_id=%s",
        name_in_log.user(callback),
        callback_data.dist_id,
        callback_data.chat_id,
    )

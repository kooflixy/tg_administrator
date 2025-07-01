from logging import getLogger

from aiogram import Router
from aiogram.types import CallbackQuery

from app.keyboards.settings.distribution import (
    AddDistributionChatCD,
    AddDistributionChatListCD,
    add_distribution_chat_list_ikb,
)
from db.database import async_session_factory
from db.queries.distribution_chat_orm import DistributionChatORMHandler

log = getLogger(__name__)

router = Router()


@router.callback_query(AddDistributionChatListCD.filter())
async def get_add_distribution_chat_list(
    callback: CallbackQuery, callback_data: AddDistributionChatListCD
):

    # Получение списка чатов для страницы
    async with async_session_factory() as session:
        chat_list = await DistributionChatORMHandler.get_unassigned_chat_page(
            session, callback_data.cur_page, dist_id=callback_data.dist_id
        )
        is_last_page = await DistributionChatORMHandler.is_last_unassigned_chat_page(
            session, page=callback_data.cur_page, dist_id=callback_data.dist_id
        )

    await callback.message.edit_text(
        "➕Нажмите на чат, который хотите добавить:",
        reply_markup=add_distribution_chat_list_ikb(
            chat_list,
            back_page=callback_data.back_page,
            page=callback_data.cur_page,
            dist_id=callback_data.dist_id,
            is_last_page=is_last_page,
        ),
    )


@router.callback_query(AddDistributionChatCD.filter())
async def add_distribution_chat(
    callback: CallbackQuery, callback_data: AddDistributionChatCD
):

    async with async_session_factory() as session:
        await DistributionChatORMHandler.insert(
            session, chat_id=callback_data.chat_id, dist_id=callback_data.dist_id
        )
        await session.commit()

    await callback.answer("Чат добавлен в рассылку✅")

    await get_add_distribution_chat_list(
        callback,
        AddDistributionChatListCD(
            cur_page=callback_data.back_page, back_page=1, dist_id=callback_data.dist_id
        ),
    )

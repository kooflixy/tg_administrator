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


@router.callback_query(DistributionChatListCD.filter())
async def get_distribution_chat_list(
    callback: CallbackQuery, callback_data: DistributionChatListCD
):
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


@router.callback_query(RemoveDistributionChatCD.filter())
async def remove_distribution_chat(
    callback: CallbackQuery, callback_data: RemoveDistributionChatCD
):
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

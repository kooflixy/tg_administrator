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


@router.callback_query(DistributionListCD.filter())
async def get_distribution_list(
    callback: CallbackQuery, callback_data: DistributionListCD
):

    log.debug(
        "%s запросил %s страницу списка рассылок",
        name_in_log.user(callback),
        callback_data.cur_page,
    )

    # Получение списка рассылок для страницы
    async with async_session_factory() as session:
        dist_list = await DistributionORMHandler.get_page(
            session, callback_data.cur_page
        )
        is_last_page = await DistributionORMHandler.is_last_page(
            session, callback_data.cur_page
        )

    await callback.message.edit_text(
        "📋Список рассылок:",
        reply_markup=distribution_list_ikb(
            dist_list, callback_data.cur_page, is_last_page
        ),
    )
    log.info(
        "%s получил страницу списка рассылок page=%s",
        name_in_log.user(callback),
        callback_data.cur_page,
    )


@router.callback_query(DistributionDetailsCD.filter())
async def get_distribution_details(
    callback: CallbackQuery, callback_data: DistributionDetailsCD
):
    """Отображение деталей рассылки"""

    async with async_session_factory() as session:
        dist = await DistributionORMHandler.get(session, callback_data.dist_id)

    if not dist:
        await callback.answer("Такой рассылки нет")
        return

    await callback.message.edit_text(
        text=f"""Название: {dist.name}
Интервал: {dist.interval}
""",
        reply_markup=distribution_details_ikb(
            dist=dist, back_page=callback_data.back_page
        ),
    )


@router.callback_query(ShowDistributionCD.filter())
async def show_distribution(callback: CallbackQuery, callback_data: ShowDistributionCD):
    """Отображение сообщения рассылки"""

    async with async_session_factory() as session:
        dist = await DistributionORMHandler.get(session, callback_data.dist_id)

    if not dist:
        await callback.answer("Такой рассылки нет")
        return

    try:
        await bot.copy_message(
            callback.message.chat.id, callback.message.chat.id, dist.msg_id
        )
    except TelegramBadRequest:
        await callback.answer("Сообщение было удалено")


@router.callback_query(ChangeDistributionActivityCD.filter())
async def change_distribution_activity(
    callback: CallbackQuery, callback_data: ChangeDistributionActivityCD
):
    """Изменение активности рассылки"""

    async with async_session_factory() as session:
        await DistributionORMHandler.change_activity(session, callback_data.dist_id)
        await session.commit()
        dist = await DistributionORMHandler.get(session, callback_data.dist_id)

    await callback.message.edit_reply_markup(
        reply_markup=distribution_details_ikb(
            back_page=callback_data.back_page, dist=dist
        )
    )


@router.callback_query(RemoveDistributionCD.filter())
async def remove_distribtution(
    callback: CallbackQuery, callback_data: RemoveDistributionCD
):
    """Удаление рассылки"""

    async with async_session_factory() as session:
        await DistributionORMHandler.remove(session, callback_data.dist_id)
        await session.commit()

    await callback.answer("Рассылка удалена")

    await get_distribution_list(
        callback, DistributionListCD(cur_page=callback_data.back_page)
    )


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

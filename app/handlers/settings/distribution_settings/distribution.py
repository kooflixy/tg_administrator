from datetime import timedelta
from logging import getLogger

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from app.bot_obj import bot
from app.keyboards.settings.distribution import (
    ChangeDistributionActivityCD,
    DistributionDetailsCD,
    RemoveDistributionCD,
    ShowDistributionCD,
    distribution_details_ikb,
    distribution_list_ikb,
)
from app.keyboards.settings_menu import DistributionListCD
from app.utils.contrib import time_text_to_seconds
from app.utils.for_logging import name_in_log
from config import settings
from db.database import async_session_factory
from db.models import DistributionORM
from db.queries.distribution_orm import DistributionORMHandler

log = getLogger(__name__)

router = Router()


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
    log.debug(
        "%s запросил детали рассылки dist_id=%s",
        name_in_log.user(callback),
        callback_data.dist_id,
    )

    async with async_session_factory() as session:
        dist = await DistributionORMHandler.get(session, callback_data.dist_id)

    if not dist:
        await callback.answer("Такой рассылки нет")
        return

    await callback.message.edit_text(
        text=f"""Название: {dist.name}
ID: {dist.id}
Интервал: {dist.interval}
""",
        reply_markup=distribution_details_ikb(
            dist=dist, back_page=callback_data.back_page
        ),
    )
    log.info(
        "%s получил детали рассылки dist_id=%s",
        name_in_log.user(callback),
        callback_data.dist_id,
    )


@router.callback_query(ShowDistributionCD.filter())
async def show_distribution(callback: CallbackQuery, callback_data: ShowDistributionCD):
    """Отображение сообщения рассылки"""

    try:
        await bot.copy_message(
            callback.message.chat.id, callback.message.chat.id, callback_data.msg_id
        )
    except TelegramBadRequest:
        await callback.answer("Сообщение было удалено")


@router.callback_query(ChangeDistributionActivityCD.filter())
async def change_distribution_activity(
    callback: CallbackQuery, callback_data: ChangeDistributionActivityCD
):
    """Изменение активности рассылки"""
    log.debug(
        "%s попытался поменять активность рассылки dist_id=%s",
        name_in_log.user(callback),
        callback_data.dist_id,
    )

    async with async_session_factory() as session:
        await DistributionORMHandler.change_activity(session, callback_data.dist_id)
        await session.commit()
        dist = await DistributionORMHandler.get(session, callback_data.dist_id)

    await callback.message.edit_reply_markup(
        reply_markup=distribution_details_ikb(
            back_page=callback_data.back_page, dist=dist
        )
    )
    log.info(
        "%s поменял активность рассылки dist_id=%s",
        name_in_log.user(callback),
        callback_data.dist_id,
    )


@router.callback_query(RemoveDistributionCD.filter())
async def remove_distribtution(
    callback: CallbackQuery, callback_data: RemoveDistributionCD
):
    """Удаление рассылки"""
    log.debug(
        "%s пытается удалить рассылку dist_id=%s",
        name_in_log.user(callback),
        callback_data.dist_id,
    )

    async with async_session_factory() as session:
        await DistributionORMHandler.remove(session, callback_data.dist_id)
        await session.commit()

    await callback.answer("Рассылка удалена")

    await get_distribution_list(
        callback, DistributionListCD(cur_page=callback_data.back_page)
    )
    log.info(
        "%s удалил рассылку dist_id=%s",
        name_in_log.user(callback),
        callback_data.dist_id,
    )


@router.message(Command("set_dist_int"))
async def set_distribution_interval(message: Message, command: CommandObject):

    # Проверка, является ли пользователь главным админом
    if message.chat.id != settings.ADMIN_ID:
        return

    if not command.args:
        return

    dist_id = command.args.split()[0]
    if not dist_id.isdigit():
        return
    dist_id = int(dist_id)

    log.debug(
        "%s пытается поменять интервал рассылки dist_id=%s",
        name_in_log.user(message),
        dist_id,
    )

    interval = time_text_to_seconds(" ".join(command.args.split()[1:]))

    if not interval:
        return

    interval = timedelta(seconds=interval)

    async with async_session_factory() as session:
        dist = await session.get(DistributionORM, dist_id)

        if not dist:
            return

        dist.interval = interval
        await message.answer(
            f"Интервал рассылки <b>{dist.name}</b> изменен на {interval}"
        )
        await session.commit()

    log.info(
        "%s поменял интервал рассылки dist_id=%s",
        name_in_log.user(message),
        dist_id,
    )

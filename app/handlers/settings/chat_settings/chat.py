from logging import getLogger

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import CallbackQuery, ChatPermissions

from app.bot_obj import bot
from app.keyboards.perm import ChangePermCD
from app.keyboards.settings.chat import (
    ChangeChatPermCD,
    ChatDetailsCD,
    ChatPermCD,
    RemoveChatCD,
    chat_details_ikb,
    chat_list_ikb,
    get_chat_perm_list_ikb,
)
from app.keyboards.settings_menu import ChatListCD
from app.utils.answer_templates import error_cb_ans
from app.utils.for_logging import name_in_log
from app.utils.perm import permissions_to_dict, redistribute_dict
from db.database import async_session_factory
from db.queries.chat_orm import ChatORMHandler

log = getLogger(__name__)

router = Router()


@router.callback_query(ChatListCD.filter())
async def get_chat_list(callback: CallbackQuery, callback_data: ChatListCD):
    """Инлайн-клавиатура списка чатов в настройках"""
    log.debug(
        "%s запросил %s страницу списка чатов",
        name_in_log.user(callback),
        callback_data.cur_page,
    )

    # Получение списка чатов для страницы
    try:
        async with async_session_factory() as session:
            chat_list = await ChatORMHandler.get_page(session, callback_data.cur_page)
            is_last_page = await ChatORMHandler.is_last_page(
                session, callback_data.cur_page
            )
    except:
        await error_cb_ans(callback)
        log.exception(
            "При попытке получить страницу чатов произошла ошибка page=%s",
            callback_data.cur_page,
        )
        return

    await callback.message.edit_text(
        "📋Список отслеживаемых чатов:",
        reply_markup=chat_list_ikb(chat_list, callback_data.cur_page, is_last_page),
    )
    log.info(
        "%s получил %s страницу списка чатов",
        name_in_log.user(callback),
        callback_data.cur_page,
    )


@router.callback_query(ChatDetailsCD.filter())
async def get_chat_details(callback: CallbackQuery, callback_data: ChatDetailsCD):
    """Детали чата, выбранного в списке чатов"""

    log.debug(
        "%s запросил детали отслеживаемого чата chat_id=%s",
        name_in_log.user(callback),
        callback_data.chat_id,
    )

    # Получение чата
    try:
        async with async_session_factory() as session:
            chat = await ChatORMHandler.get(session, callback_data.chat_id)
    except:
        await error_cb_ans(callback)
        log.exception(
            "При попытке получить детали чата произошла ошибка chat_id=%s",
            callback_data.chat_id,
        )
        return

    # Проверка, отслеживается ли чат
    if not chat:
        await callback.answer("Этот чат не отслеживается")
        log.info(
            "%s запросил детали отслеживаемого чата, но он не отслеживается chat_id=%s",
            name_in_log.user(callback),
            callback_data.chat_id,
        )
        return

    await callback.message.edit_text(
        f"Чат: <code>{chat.name}</code>\nID: <code>{chat.id}</code>",
        reply_markup=chat_details_ikb(chat.id, callback_data.back_page),
    )
    log.info(
        "%s получил детали отслеживаемого чата chat_id=%s",
        name_in_log.user(callback),
        callback_data.chat_id,
    )


@router.callback_query(RemoveChatCD.filter())
async def remove_chat(callback: CallbackQuery, callback_data: RemoveChatCD):
    """Удаление чата из отслеживаемых"""
    log.debug(
        "%s начал удаление чата из отслеживаемых chat_id=%s",
        name_in_log.user(callback),
        callback_data.chat_id,
    )

    try:
        async with async_session_factory() as session:
            await ChatORMHandler.remove(session, callback_data.chat_id)
            await session.commit()
    except:
        await error_cb_ans(callback)
        log.exception(
            "При попытке удалить отслеживаемый чат произошла ошибка chat_id=%s",
            callback_data.chat_id,
        )
        return

    await callback.answer("Чат больше не отслеживается")

    await get_chat_list(callback, ChatListCD(cur_page=callback_data.back_page))
    log.info(
        "%s удалил чат из отслеживаемых chat_id: %s",
        name_in_log.user(callback),
        callback_data.chat_id,
    )


@router.callback_query(ChatPermCD.filter())
async def get_chat_perm(callback: CallbackQuery, callback_data: ChatPermCD):
    async with async_session_factory() as session:
        chat = await ChatORMHandler.get(session, callback_data.chat_id)
        if chat.perms:
            chat_perms = chat.perms
        else:
            chat_perms = (await bot.get_chat(callback_data.chat_id)).permissions
        chat_perms = permissions_to_dict(chat_perms)

    try:
        await callback.message.edit_text(
            f"Права участников в <b>{chat.name}</b>:",
            reply_markup=get_chat_perm_list_ikb(
                chat_perms, callback_data.chat_id, back_page=callback_data.back_page
            ),
        )
    except TelegramBadRequest:
        pass
    except TelegramRetryAfter:
        await callback.answer("Слишком много изменений, попробуйте позже")


@router.callback_query(ChangeChatPermCD.filter())
async def change_chat_perm(callback: CallbackQuery, callback_data: ChangeChatPermCD):

    async with async_session_factory() as session:
        chat = await ChatORMHandler.get(session, callback_data.chat_id)
        if chat.perms:
            chat_perms = chat.perms
        else:
            tchat = await bot.get_chat(callback_data.chat_id)
            chat_perms = tchat.permissions
        chat_perms = permissions_to_dict(chat_perms)

        chat_perms[callback_data.perm] = not chat_perms[callback_data.perm]

        if chat.perms:
            tchat = await bot.get_chat(callback_data.chat_id)

        await tchat.set_permissions(ChatPermissions(**chat_perms))

        chat_perms = permissions_to_dict(
            (await bot.get_chat(callback_data.chat_id)).permissions
        )

        ChatORMHandler.change_perms(session, chat, chat_perms)

        await session.commit()
    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_chat_perm_list_ikb(
                chat_perms, callback_data.chat_id, callback_data.back_page
            )
        )
    except TelegramBadRequest:
        pass
    except TelegramRetryAfter:
        await callback.answer("Слишком много изменений, попробуйте позже")

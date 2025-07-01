from logging import getLogger

from aiogram import Router
from aiogram.types import CallbackQuery

from app.keyboards.settings.moderator import (
    AddModeratorChatCD,
    AddModeratorChatListCD,
    add_moderator_chat_list_ikb,
)
from app.utils.answer_templates import error_cb_ans
from app.utils.for_logging import name_in_log
from db.database import async_session_factory
from db.queries.chat_orm import ChatORMHandler
from db.queries.moderator_chat_orm import ModeratorChatORMHandler
from db.queries.moderator_orm import ModeratorORMHandler

log = getLogger(__name__)

router = Router()


@router.callback_query(AddModeratorChatListCD.filter())
async def get_add_moderator_chat_list(
    callback: CallbackQuery, callback_data: AddModeratorChatListCD
):
    """Отображение списка чатов, возможных для добавления в модерируемые модератора"""
    log.debug(
        "%s запросил страницу возможных для добавления в модерируемые чатов page=%s, moderator_id=%s",
        name_in_log.user(callback),
        callback_data.cur_page,
        callback_data.moderator_id,
    )

    # Получение списка чатов для страницы
    try:
        async with async_session_factory() as session:
            chat_list = await ChatORMHandler.get_unassigned_chat_page(
                session, callback_data.cur_page, callback_data.moderator_id
            )
            is_last_page = await ChatORMHandler.is_last_unassigned_chat_page(
                session,
                page=callback_data.cur_page,
                moderator_id=callback_data.moderator_id,
            )
    except:
        await error_cb_ans(callback)
        log.exception(
            "При попытке получить возможные для добавления в модерируемые чаты произошла ошибка page=%s moderator_id=%s",
            callback_data.cur_page,
            callback_data.moderator_id,
        )
        return

    await callback.message.edit_text(
        "➕Нажмите на чат, который хотите добавить:",
        reply_markup=add_moderator_chat_list_ikb(
            chat_list,
            back_page=callback_data.back_page,
            page=callback_data.cur_page,
            moderator_id=callback_data.moderator_id,
            is_last_page=is_last_page,
        ),
    )
    log.info(
        "%s получил страницу возможных для добавления в модерируемые чатов page=%s, moderator_id=%s",
        name_in_log.user(callback),
        callback_data.cur_page,
        callback_data.moderator_id,
    )


@router.callback_query(AddModeratorChatCD.filter())
async def add_moderator_chat(
    callback: CallbackQuery, callback_data: AddModeratorChatCD
):
    """Добавление чата в модерирумые для модератора"""
    log.debug(
        "%s пытается добавить чат в модерируемые к модератору moderator_id=%s, chat_is=%s",
        name_in_log.user(callback),
        callback_data.moderator_id,
        callback_data.chat_id,
    )

    try:
        async with async_session_factory() as session:
            # Проверка, является ли пользователь модератором
            if not await ModeratorORMHandler.get(session, callback_data.moderator_id):
                await callback.answer("Пользователь не является модератором")
                log.info(
                    "%s пытался добавить чат в модерируемые пользователю, не являющемуся модератором moderator_id=%s, chat_id=%s",
                    name_in_log.user(callback),
                    callback_data.moderator_id,
                    callback_data.chat_id,
                )
                return

            # Проверка, не является ли этот чат уже модерируемым этим модератором
            if await ModeratorChatORMHandler.get_by_moderator_and_chat_ids(
                session,
                moderator_id=callback_data.moderator_id,
                chat_id=callback_data.chat_id,
            ):
                await callback.answer("Пользователь уже модерирует этот чат")
                log.info(
                    "%s пытался добавить в модерируемые пользователю уже модерируемый чат moderator_id=%s, chat_id=%s",
                    name_in_log.user(callback),
                    callback_data.moderator_id,
                    callback_data.chat_id,
                )
                return

            await ModeratorChatORMHandler.insert(
                session,
                moderator_id=callback_data.moderator_id,
                chat_id=callback_data.chat_id,
            )

            await session.commit()
    except:
        await error_cb_ans(callback)
        log.exception(
            "При попытке добавить чат в модерируемые к модератору moderator_id=%s, chat_is=%s",
            callback_data.moderator_id,
            callback_data.chat_id,
        )
        return

    await callback.answer("Чат добавлен в модерируемые✅")

    await get_add_moderator_chat_list(
        callback,
        AddModeratorChatListCD(
            moderator_id=callback_data.moderator_id, cur_page=callback_data.back_page
        ),
    )
    log.info(
        "%s добавил чат в модерируемые пользователю moderator_id=%s, chat_id=%s",
        name_in_log.user(callback),
        callback_data.moderator_id,
        callback_data.chat_id,
    )

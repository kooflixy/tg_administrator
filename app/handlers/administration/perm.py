from logging import getLogger

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, ChatMemberRestricted, ChatPermissions, Message

from app.bot_obj import bot
from app.keyboards.perm import ChangePermCD, ResetPermCD, get_perm_list_ikb
from app.utils.checkers import RestChecker
from app.utils.contrib import get_user_id_name_reason
from app.utils.perm import permissions_to_dict
from app.utils.rest_handler.mute_rest import MuteRestHandler
from app.utils.rest_handler.perm_rest import PermRestHandler
from app.utils.text_markup import TextMarkup
from db.database import async_session_factory
from db.models import UserPermORM
from db.queries.chat_orm import ChatORMHandler

router = Router()

log = getLogger(__name__)


@router.message(Command("perm"))
async def get_user_perm(message: Message, command: CommandObject):
    if not await ChatORMHandler.is_chat_monitored(message.chat.id):
        return

    if not await PermRestHandler.is_perm_exists(message.from_user.id, message.chat.id):
        return

    # Получение пользователя
    user, etc = await get_user_id_name_reason(message, command)

    # Проверка, является ли пользователь текущим ботом
    if await RestChecker.is_user_main_bot(user.id, message):
        return

    chat_member = await bot.get_chat_member(message.chat.id, user.id)

    # Проверка, является ли пользователь участником группы
    if not await RestChecker.is_user_member(chat_member, message):
        return

    # Проверка, является ли пользователь модератором чата
    if await RestChecker.is_user_moderator(chat_member, message):
        return

    async with async_session_factory() as session:
        user_perms = await PermRestHandler.get_by_user_chat_ids(
            session, user.id, message.chat.id
        )
        if user_perms:
            user_perms = permissions_to_dict(user_perms)
        else:
            chat = await bot.get_chat(message.chat.id)
            user_perms = permissions_to_dict(chat.permissions)
        await message.reply(
            f"Права {TextMarkup.tag_user(user.name, user.id)}:",
            reply_markup=get_perm_list_ikb(user_perms, message.chat.id, user.id),
        )


@router.callback_query(ChangePermCD.filter())
async def change_user_perm(callback: CallbackQuery, callback_data: ChangePermCD):

    if not await PermRestHandler.is_perm_exists(
        callback.from_user.id, callback_data.chat_id
    ):
        return

    async with async_session_factory() as session:
        if await MuteRestHandler._is_rest_exists(
            session, callback_data.chat_id, callback_data.user_id
        ):
            await callback.answer("Пользователь находится в муте")
            return

        user_perms = await PermRestHandler.get_by_user_chat_ids(
            session, callback_data.user_id, callback_data.chat_id
        )
        if not user_perms:
            chat = await bot.get_chat(callback_data.chat_id)
            user_perms = chat.permissions
        user_perms = permissions_to_dict(user_perms)

        user_perms[callback_data.perm] = not user_perms[callback_data.perm]

        await bot.restrict_chat_member(
            callback_data.chat_id, callback_data.user_id, ChatPermissions(**user_perms)
        )
        user = await bot.get_chat_member(callback_data.chat_id, callback_data.user_id)
        user_perms = permissions_to_dict(user)

        await PermRestHandler.change_user_perm(
            session, callback_data.user_id, callback_data.chat_id, user_perms
        )

        await session.commit()
    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_perm_list_ikb(
                user_perms, callback_data.chat_id, callback_data.user_id
            )
        )
    except TelegramBadRequest:
        pass


@router.callback_query(ResetPermCD.filter())
async def reset_user_perm(callback: CallbackQuery, callback_data: ResetPermCD):
    if not await PermRestHandler.is_perm_exists(
        callback.from_user.id, callback_data.chat_id
    ):
        return

    async with async_session_factory() as session:
        if await MuteRestHandler._is_rest_exists(
            session, callback_data.chat_id, callback_data.user_id
        ):
            await callback.answer("Пользователь находится в муте")
            return

        user_perms = await PermRestHandler.get_by_user_chat_ids(
            session, callback_data.user_id, callback_data.chat_id
        )

        if user_perms:
            await session.delete(user_perms)
            await session.commit()

        await bot.promote_chat_member(callback_data.chat_id, callback_data.user_id)

    await callback.answer("Права успешно сброшены")

    chat_perms = (await bot.get_chat(callback_data.chat_id)).permissions
    chat_perms = permissions_to_dict(chat_perms)

    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_perm_list_ikb(
                chat_perms, callback_data.chat_id, callback_data.user_id
            )
        )
    except TelegramBadRequest:
        pass
    except TelegramRetryAfter:
        await callback.answer("Слишком много изменений, попробуйте позже")

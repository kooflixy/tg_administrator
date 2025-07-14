from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.contrib import *
from app.keyboards.perm import get_emoji, get_perm_list_ikb
from app.keyboards.settings_menu import ChatListCD, SettingsListCD
from app.utils.pagination import get_paginator_ikb
from app.utils.perm import permissions_translations, redistribute_dict
from db.models import ChatORM


class ChatCDArgs(ChatIDArg, BackPageArg): ...


class ChatDetailsCD(CallbackData, ChatCDArgs, prefix="chat_d"): ...


class AddChatCD(CallbackData, prefix="add_chat"): ...


class RemoveChatCD(CallbackData, ChatCDArgs, prefix="remove_chat"): ...


class ChatPermCD(CallbackData, ChatCDArgs, BackPageArg, prefix="chchp"): ...


class ChangeChatPermCD(
    CallbackData, ChatIDArg, PermNameArg, BackPageArg, prefix="ch_u_p"
): ...


def chat_list_ikb(chat_list: list[ChatORM], page: int, is_last_page: bool):
    """Создание инлайн-клавиатуры со списком отслеживаемых чатов
    Кнопки: добавить чат; список чатов; пагинация списка чатов; назад(в меню настроек)
    Появляется при: нажатии на список чатов в меню настроек; возвращении назад"""

    builder = InlineKeyboardBuilder()
    builder.button(text="➕Добавить чат", callback_data=AddChatCD().pack())
    for chat in chat_list:
        builder.button(
            text=chat.name,
            callback_data=ChatDetailsCD(back_page=page, chat_id=chat.id).pack(),
        )
    builder.attach(
        get_paginator_ikb(ChatListCD, cur_page=page, is_last_page=is_last_page)
    )
    builder.attach(back_ibtn(SettingsListCD()))
    builder.adjust(1, *([1] * len(chat_list)), 3, 1)

    return builder.as_markup()


def get_chat_perm_list_ikb(perms: dict, chat_id: int, back_page: int = 1):
    builder = InlineKeyboardBuilder()

    perms = redistribute_dict(perms)
    for perm in perms.keys():
        emoji = get_emoji(perms[perm])
        ru_perm = permissions_translations[perm]
        builder.button(
            text=emoji + ru_perm,
            callback_data=ChangeChatPermCD(
                perm=perm, chat_id=chat_id, back_page=back_page
            ).pack(),
        )
    builder.attach(back_ibtn(ChatDetailsCD(back_page=back_page, chat_id=chat_id)))
    builder.adjust(*([2] * 7), 1)
    return builder.as_markup()


def chat_details_ikb(chat_id: int, back_page: int):
    """Создание инлайн-клавиатуры с деталями отслеживаемого чата
    Кнопки: удалить чат; назад(в список чатов)
    Появляется при: нажатии на определенный чат в списке чатов; возвращении назад"""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="🪪Права участников",
        callback_data=ChatPermCD(back_page=back_page, chat_id=chat_id),
    )
    builder.button(
        text="❌Удалить",
        callback_data=RemoveChatCD(chat_id=chat_id, back_page=back_page).pack(),
    )
    builder.attach(back_ibtn(ChatListCD(cur_page=back_page)))
    builder.adjust(
        1,
        1,
        1,
    )

    return builder.as_markup()

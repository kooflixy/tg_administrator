from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.contrib import *
from app.keyboards.settings_menu import ChatListCD, SettingsListCD
from app.utils.pagination import get_paginator_ikb
from db.models import ChatORM


class ChatCDArgs(ChatIDArg, BackPageArg): ...


class ChatDetailsCD(CallbackData, ChatCDArgs, prefix="chat_d"): ...


class AddChatCD(CallbackData, prefix="add_chat"): ...


class RemoveChatCD(CallbackData, ChatCDArgs, prefix="remove_chat"): ...


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


def chat_details_ikb(chat_id: int, back_page: int):
    """Создание инлайн-клавиатуры с деталями отслеживаемого чата
    Кнопки: удалить чат; назад(в список чатов)
    Появляется при: нажатии на определенный чат в списке чатов; возвращении назад"""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌Удалить",
        callback_data=RemoveChatCD(chat_id=chat_id, back_page=back_page).pack(),
    )
    builder.attach(back_ibtn(ChatListCD(cur_page=back_page)))

    return builder.as_markup()

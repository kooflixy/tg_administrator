from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.settings_menu import ChatListCD, SettingsListCD
from app.keyboards.contrib import get_paginator_ikb
from db.models import ChatORM

class AddChatCD(CallbackData, prefix='add_chat'): ...

class ChatCDArgs:
    chat_id: int
    page: int

class RemoveChatCD(ChatCDArgs, CallbackData, prefix='remove_chat'): ...

class ChatDetailsCD(ChatCDArgs, CallbackData, prefix='chat_d'): ...

def chat_list_ikb(chat_list: list[ChatORM], page: int):
    # Создание клавиатуры кнопок

    builder = InlineKeyboardBuilder()
    builder.button(text='Добавить чат', callback_data=AddChatCD().pack())
    for chat in chat_list:
        builder.button(text=chat.name, callback_data=ChatDetailsCD(chat_id=chat.id, page=page).pack())
    builder.button(text='⬅', callback_data=SettingsListCD().pack())
    builder.attach(InlineKeyboardBuilder.from_markup(get_paginator_ikb(page, ChatListCD)))
    builder.adjust(1, *([1]*len(chat_list)), 4)

    return builder.as_markup()

def chat_details_ikb(chat_id: int, page: int):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='❌Удалить', callback_data=RemoveChatCD(chat_id=chat_id, page=page).pack())],
            [InlineKeyboardButton(text='⬅', callback_data=ChatListCD(page=page).pack())],
        ]
    )
    return kb

def removed_chat_details_ikb(page: int):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='⬅', callback_data=ChatListCD(page=page).pack())],
        ]
    )
    return kb
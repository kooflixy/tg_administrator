from typing import Optional
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.contrib import *
from app.keyboards.settings_menu import ModeratorListCD, SettingsListCD
from db.models import ChatORM, ModeratorORM, LnkChatModeratorORM

class AddModeratorCD(CallbackData, prefix='add_moderator'): ...

class ModerCDArgs:
    moderator_id: int
    page: int = 1

class RemoveModeratorCD(ModerCDArgs, CallbackData, prefix='remove_moderator'): ...

class ModeratorDetailsCD(ModerCDArgs, CallbackData, prefix='moderator_d'): ...

class ModeratorChatsListCD(ModerCDArgs, CallbackData, prefix='moderator_ch_lst'): ...

class AddModeratorChatListCD(ModerCDArgs, CallbackData, prefix='add_moderator_ch_l'): ...

class AddModeratorChatCD(ModerCDArgs, CallbackData, prefix='add_moderator_ch'):
    chat_id: int

class ModeratorChatDetailsCD(ModerCDArgs, CallbackData, prefix='moderator_ch_d'):
    chat_id: int

class RemoveModeratorChatCD(ModerCDArgs, CallbackData, prefix='remove_moderator_ch'):
    chat_id: int

class ChangeModeratorChatPermissionCD(ModerCDArgs, CallbackData, prefix='change_m_ch_perm'):
    chat_id: int
    perm_name: str


def moderator_list_ikb(moderator_list: list[ModeratorORM], page: int):
    # Создание клавиатуры кнопок

    builder = InlineKeyboardBuilder()
    builder.button(text='Добавить модератора', callback_data=AddModeratorCD().pack())
    for moderator in moderator_list:
        builder.button(text=moderator.name, callback_data=ModeratorDetailsCD(moderator_id=moderator.id, page=page).pack())
    builder.button(text='⬅', callback_data=SettingsListCD().pack())
    builder.attach(InlineKeyboardBuilder.from_markup(get_paginator_ikb(page, ModeratorListCD)))
    builder.adjust(1, *([1]*len(moderator_list)), 4)

    return builder.as_markup()

def moderator_details_ikb(moderator_id: int, page: int):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Чаты', callback_data=ModeratorChatsListCD(moderator_id=moderator_id, page=page).pack())],
            [
                InlineKeyboardButton(text='⬅', callback_data=ModeratorListCD().pack()), 
                InlineKeyboardButton(text='❌Удалить', callback_data=RemoveModeratorCD(moderator_id=moderator_id, page=page).pack())
            ],
        ]
    )
    return kb

def removed_moderator_details_ikb(page: int):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='⬅', callback_data=ModeratorListCD(page=page).pack())],
        ]
    )
    return kb

def moderator_chat_list_ikb(chat_list: list[LnkChatModeratorORM], page: int, moderator_id: int):
    # Создание клавиатуры кнопок
    
    builder = InlineKeyboardBuilder()
    builder.button(text='Добавить чат', callback_data=AddModeratorChatListCD(moderator_id=moderator_id).pack())
    for chat in chat_list:
        builder.button(text=chat.chat.name, callback_data=ModeratorChatDetailsCD(moderator_id=chat.moderator_id, chat_id=chat.chat_id, page=page).pack())
    builder.button(**back_ibtn(ModeratorDetailsCD(moderator_id=moderator_id)))
    builder.attach(InlineKeyboardBuilder.from_markup(get_paginator_ikb(page, ModeratorChatsListCD, moderator_id=moderator_id)))
    builder.adjust(1, *([1]*len(chat_list)), 4)

    return builder.as_markup()

def add_moderator_chat_list_ikb(chat_list: list[ChatORM], page: int, moderator_id: int):
    # Создание клавиатуры кнопок
    
    builder = InlineKeyboardBuilder()
    for chat in chat_list:
        builder.button(text=chat.name, callback_data=AddModeratorChatCD(moderator_id=moderator_id, chat_id=chat.id).pack())
    builder.button(**back_ibtn(ModeratorChatsListCD(moderator_id=moderator_id)))
    builder.attach(InlineKeyboardBuilder.from_markup(get_paginator_ikb(page, AddModeratorChatListCD, moderator_id=moderator_id)))
    builder.adjust(*([1]*len(chat_list)), 4)

    return builder.as_markup()

def moderator_permissions_ikb(moderator: LnkChatModeratorORM):

    builder = InlineKeyboardBuilder()
    for perm_ru_name, perm_db_name, is_perm_exists in zip(['Бан по сети чатов', 'Бан', 'Кик', 'Мут', 'Варн'],
                                ['ba_perm', 'ban_perm', 'kick_perm', 'mute_perm', 'warn_perm'],
                                [moderator.ba_perm, moderator.ban_perm, moderator.kick_perm, moderator.mute_perm, moderator.warn_perm]):
        emoji = '✅' if is_perm_exists else '❌'
        text  =  ' '.join([emoji, perm_ru_name, emoji])
        builder.button(text=text, callback_data=ChangeModeratorChatPermissionCD(moderator_id=moderator.moderator_id, chat_id=moderator.chat_id, perm_name=perm_db_name))
    builder.button(**back_ibtn(ModeratorChatsListCD(moderator_id=moderator.moderator_id)))
    builder.button(text='Удалить', callback_data=RemoveModeratorChatCD(moderator_id=moderator.moderator_id, chat_id=moderator.chat_id).pack())
    builder.adjust(*([1]*5, 2))

    return builder.as_markup()
from dataclasses import dataclass
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.contrib import *
from app.keyboards.settings_menu import ModeratorListCD, SettingsListCD
from app.utils.pagination import get_paginator_ikb
from db.models import ChatORM, ModeratorChatORM, ModeratorORM


# Действия с модераторами
class ModeratorDetailsCD(
    CallbackData, ModerIdArg, BackPageArg, prefix="moderator_d"
): ...


class AddModeratorCD(CallbackData, prefix="add_moderator"): ...


class RemoveModeratorCD(
    CallbackData, ModerIdArg, BackPageArg, prefix="remove_moderator"
): ...


# Действия с чатами модератора
class ModeratorChatListCD(
    CallbackData, ModerIdArg, CurrentPageArg, prefix="moderator_ch_lst"
): ...


class ModeratorChatDetailsCD(
    CallbackData, ModerIdArg, BackPageArg, ModerChatIdCDArg, prefix="moderator_ch_d"
): ...


class AddModeratorChatListCD(
    CallbackData, ModerIdArg, BackPageArg, CurrentPageArg, prefix="add_moderator_ch_l"
): ...


class AddModeratorChatCD(
    CallbackData, ModerIdArg, ModerChatIdCDArg, BackPageArg, prefix="add_moderator_ch"
): ...


class RemoveModeratorChatCD(
    CallbackData,
    ModerIdArg,
    ModerChatIdCDArg,
    BackPageArg,
    prefix="remove_moderator_ch",
): ...


class ChangeModeratorChatPermissionCD(
    CallbackData, ModerIdArg, ModerChatIdCDArg, BackPageArg, prefix="change_m_ch_perm"
):
    perm_name: str


def moderator_list_ikb(
    moderator_list: list[ModeratorORM], page: int, is_last_page: bool
):
    """Создание инлайн-клавиатуры со списком модераторов
    Кнопки: добавление модератора; список модераторов, пагинация; назад(в меню настроек)
    Появляется при: нажатии на список модераторов в настройках; пагинации списка модераторов; возвращении назад
    """

    builder = InlineKeyboardBuilder()
    builder.button(text="➕Добавить модератора", callback_data=AddModeratorCD().pack())
    for moderator in moderator_list:
        builder.button(
            text=moderator.name,
            callback_data=ModeratorDetailsCD(
                moderator_id=moderator.id, back_page=page
            ).pack(),
        )
    builder.attach(
        get_paginator_ikb(ModeratorListCD, cur_page=page, is_last_page=is_last_page)
    )
    builder.attach(back_ibtn(SettingsListCD()))
    builder.adjust(1, *([1] * len(moderator_list)), 3, 1)

    return builder.as_markup()


def moderator_details_ikb(moderator_id: int, back_page: int = 1):
    """Создание инлайн-клавиатуры с деталями определенного модератора
    Кнопки: просмотр списка модерируемых чатов; разжалование, назад(в список модераторов)
    Появляется при: нажатии на модератора в списке модераторов; возвращении назад"""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="📋Чаты",
        callback_data=ModeratorChatListCD(cur_page=1, moderator_id=moderator_id).pack(),
    )
    builder.button(
        text="❌Разжаловать",
        callback_data=RemoveModeratorCD(
            moderator_id=moderator_id, back_page=back_page
        ).pack(),
    )
    builder.attach(back_ibtn(ModeratorListCD(cur_page=back_page)))
    builder.adjust(1, 1, 1)

    return builder.as_markup()


def moderator_chat_list_ikb(
    chat_list: list[ModeratorChatORM], page: int, moderator_id: int, is_last_page: bool
):
    """Создание инлайн-клавиатуры со списокм модерируемых чатов выбранного модератора
    Кнопки: добавить модерируемый чат; список модерируемых чатов модератора; назад(в детали модератора)
    Появляется при: нажатии на просмотр списка модерируемых чатов; пагинации списка модерируемых чатов; возвращении назад
    """

    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕Добавить чат",
        callback_data=AddModeratorChatListCD(
            cur_page=1, back_page=page, moderator_id=moderator_id
        ).pack(),
    )
    for chat in chat_list:
        builder.button(
            text=chat.chat.name,
            callback_data=ModeratorChatDetailsCD(
                chat_id=chat.chat_id, back_page=page, moderator_id=chat.moderator_id
            ).pack(),
        )
    builder.attach(
        get_paginator_ikb(
            ModeratorChatListCD,
            cur_page=page,
            moderator_id=moderator_id,
            is_last_page=is_last_page,
        )
    )
    builder.attach(
        back_ibtn(ModeratorDetailsCD(back_page=1, moderator_id=moderator_id))
    )
    builder.adjust(1, *([1] * len(chat_list)), 3, 1)

    return builder.as_markup()


def add_moderator_chat_list_ikb(
    chat_list: list[ChatORM],
    back_page: int,
    page: int,
    moderator_id: int,
    is_last_page: bool,
):
    """Создание инлайн-клавиатуры со списокм чатов, возможных для добавления в модерируемые определенному модератору
    Кнопки: список чатов, возможных для добавления в модерируемые; назад(в список модерируемых чатов модератора)
    Появляется при: нажатии на кнопку "Добавить чат" в списке модерируемых чатов модератора
    """

    builder = InlineKeyboardBuilder()
    for chat in chat_list:
        builder.button(
            text=chat.name,
            callback_data=AddModeratorChatCD(
                back_page=page, chat_id=chat.id, moderator_id=moderator_id
            ).pack(),
        )
    builder.attach(
        get_paginator_ikb(
            AddModeratorChatListCD,
            cur_page=page,
            back_page=back_page,
            moderator_id=moderator_id,
            is_last_page=is_last_page,
        )
    )
    builder.attach(
        back_ibtn(ModeratorChatListCD(cur_page=back_page, moderator_id=moderator_id))
    )
    builder.adjust(*([1] * len(chat_list)), 3, 1)

    return builder.as_markup()


def moderator_chat_details_ikb(moderator: ModeratorChatORM, back_page: int):
    """Создание инлайн-клавиатуры с деталями модерируемого чата модератора
    Кнопки: права модератора(можно изменить при нажатии); удалить чат из модерируемых этого модератора; назад(в список модерируемых чатов модератора)
    Появляется при: нажатии на модерируемый чат в списке модерируемых чатов"""

    builder = InlineKeyboardBuilder()
    for perm_ru_name, perm_db_name, is_perm_exists in zip(
        ["Бан по сети чатов", "Бан", "Кик", "Мут", "Варн", "Закрытие/открытие чата"],
        ["ba_perm", "ban_perm", "kick_perm", "mute_perm", "warn_perm", "close_perm"],
        [
            moderator.ba_perm,
            moderator.ban_perm,
            moderator.kick_perm,
            moderator.mute_perm,
            moderator.warn_perm,
            moderator.close_perm,
        ],
    ):
        emoji = "✅" if is_perm_exists else "❌"
        text = " ".join([emoji, perm_ru_name, emoji])
        builder.button(
            text=text,
            callback_data=ChangeModeratorChatPermissionCD(
                back_page=back_page,
                moderator_id=moderator.moderator_id,
                chat_id=moderator.chat_id,
                perm_name=perm_db_name,
            ),
        )
    builder.button(
        text="Удалить",
        callback_data=RemoveModeratorChatCD(
            back_page=back_page,
            moderator_id=moderator.moderator_id,
            chat_id=moderator.chat_id,
        ).pack(),
    )
    builder.attach(
        back_ibtn(
            ModeratorChatListCD(cur_page=back_page, moderator_id=moderator.moderator_id)
        )
    )
    builder.adjust(*([1] * 5), 1, 1)

    return builder.as_markup()

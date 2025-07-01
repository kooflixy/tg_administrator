from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.contrib import *
from app.keyboards.contrib import back_ibtn
from app.keyboards.settings_menu import DistributionListCD, SettingsListCD
from app.utils.pagination import get_paginator_ikb
from db.models import ChatORM, DistributionChatORM, DistributionORM


class DistributionDetailsCD(CallbackData, DistIdArg, BackPageArg, prefix="dist_d"): ...


class DistributionChatListCD(
    CallbackData, DistIdArg, CurrentPageArg, prefix="dist_ch_l"
): ...


class RemoveDistributionCD(CallbackData, DistIdArg, BackPageArg, prefix="r_dist"): ...


class ShowDistributionCD(CallbackData, DistMsgIdArg, prefix="s_dist"): ...


class ChangeDistributionActivityCD(
    CallbackData, DistIdArg, BackPageArg, prefix="ch_a_dist"
): ...


class ChangeDistributionIntervalCD(CallbackData, DistIdArg, prefix="ch_i_dist"): ...


class DistributionChatDetailsCD(
    CallbackData, DistIdArg, ChatIDArg, BackPageArg, prefix="dist_ch_d"
): ...


class AddDistributionChatListCD(
    CallbackData, DistIdArg, BackPageArg, CurrentPageArg, prefix="add_dist_ch_l"
): ...


class AddDistributionChatCD(
    CallbackData, DistIdArg, ChatIDArg, BackPageArg, prefix="add_dist_ch"
): ...


class RemoveDistributionChatCD(
    CallbackData,
    DistIdArg,
    ChatIDArg,
    BackPageArg,
    prefix="remove_dist_ch",
): ...


def distribution_list_ikb(
    dist_list: list[DistributionORM], page: int, is_last_page: bool
):
    builder = InlineKeyboardBuilder()
    for dist in dist_list:
        builder.button(
            text=dist.name,
            callback_data=DistributionDetailsCD(dist_id=dist.id, back_page=page).pack(),
        )
    builder.attach(
        get_paginator_ikb(DistributionListCD, cur_page=page, is_last_page=is_last_page)
    )
    builder.attach(back_ibtn(SettingsListCD()))
    builder.adjust(*([1] * len(dist_list)), 3, 1)

    return builder.as_markup()


def distribution_details_ikb(dist: DistributionORM, back_page: int = 1):

    dist_status_text = "❌ Выключить" if dist.is_active else "✅ Включить"

    builder = InlineKeyboardBuilder()
    builder.button(
        text="📋Чаты",
        callback_data=DistributionChatListCD(cur_page=1, dist_id=dist.id).pack(),
    )
    builder.button(
        text="⏳Изменить интервал",
        callback_data=ChangeDistributionIntervalCD(dist_id=dist.id),
    )
    builder.button(
        text="👁Показать", callback_data=ShowDistributionCD(msg_id=dist.msg_id).pack()
    )
    builder.button(
        text=dist_status_text,
        callback_data=ChangeDistributionActivityCD(dist_id=dist.id),
    )
    builder.button(
        text="❌Удалить",
        callback_data=RemoveDistributionCD(dist_id=dist.id, back_page=back_page).pack(),
    )
    builder.attach(back_ibtn(DistributionListCD(cur_page=back_page)))
    builder.adjust(1, 2, 2, 1)

    return builder.as_markup()


def distribution_chat_list_ikb(
    dist_list: list[DistributionChatORM], page: int, dist_id: int, is_last_page: bool
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕Добавить чат",
        callback_data=AddDistributionChatListCD(
            cur_page=1, back_page=page, dist_id=dist_id
        ).pack(),
    )
    for dist in dist_list:
        builder.button(
            text=dist.chat.name,
            callback_data=RemoveDistributionChatCD(
                chat_id=dist.chat_id, back_page=page, dist_id=dist.distribution_id
            ).pack(),
        )
    builder.attach(
        get_paginator_ikb(
            DistributionChatListCD,
            cur_page=page,
            dist_id=dist_id,
            is_last_page=is_last_page,
        )
    )
    builder.attach(back_ibtn(DistributionDetailsCD(back_page=1, dist_id=dist_id)))
    builder.adjust(1, *([1] * len(dist_list)), 3, 1)

    return builder.as_markup()


def add_distribution_chat_list_ikb(
    chat_list: list[ChatORM],
    back_page: int,
    page: int,
    dist_id: int,
    is_last_page: bool,
):

    builder = InlineKeyboardBuilder()
    for chat in chat_list:
        builder.button(
            text=chat.name,
            callback_data=AddDistributionChatCD(
                back_page=page, chat_id=chat.id, dist_id=dist_id
            ).pack(),
        )
    builder.attach(
        get_paginator_ikb(
            AddDistributionChatListCD,
            cur_page=page,
            back_page=back_page,
            dist_id=dist_id,
            is_last_page=is_last_page,
        )
    )
    builder.attach(
        back_ibtn(DistributionChatListCD(cur_page=back_page, dist_id=dist_id))
    )
    builder.adjust(*([1] * len(chat_list)), 3, 1)

    return builder.as_markup()

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.contrib import *
from app.keyboards.contrib import back_ibtn
from app.keyboards.settings_menu import DistributionListCD, SettingsListCD
from app.utils.pagination import get_paginator_ikb
from db.models import DistributionORM


class DistributionDetailsCD(CallbackData, DistIdArg, BackPageArg, prefix="dist_d"): ...


class DistribtutionChatListCD(
    CallbackData, DistIdArg, CurrentPageArg, prefix="dist_ch_l"
): ...


class RemoveDistributionCD(CallbackData, DistIdArg, BackPageArg, prefix="r_dist"): ...


class ShowDistributionCD(CallbackData, DistMsgIdArg, prefix="s_dist"): ...


class ChangeDistributionActivityCD(
    CallbackData, DistIdArg, BackPageArg, prefix="ch_a_dist"
): ...


class ChangeDistributionIntervalCD(CallbackData, DistIdArg, prefix="ch_i_dist"): ...


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
    """Создание инлайн-клавиатуры с деталями определенного модератора
    Кнопки: просмотр списка модерируемых чатов; разжалование, назад(в список модераторов)
    Появляется при: нажатии на модератора в списке модераторов; возвращении назад"""

    dist_status_text = "❌ Выключить" if dist.is_active else "✅ Включить"

    builder = InlineKeyboardBuilder()
    builder.button(
        text="📋Чаты",
        callback_data=DistribtutionChatListCD(cur_page=1, dist_id=dist.id).pack(),
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
